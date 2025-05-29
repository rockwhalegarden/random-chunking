from ipfs import upload_file


class PixelChunkProcessor:
    def __init__(self, splice_indices = [1], is_encryption = True):
        self.is_encryption = is_encryption
        self.splice_indices = [0]
        self.chunk_idx = 0
        self.accumulated_bytes = 0

        for i in splice_indices:
            self.splice_indices.append(i)
        
        self.splice_chunk_size = [self.splice_indices[i] - self.splice_indices[i - 1] for i in range(1, len(self.splice_indices))]
        print(self.splice_chunk_size)
        self.current_chunk_size = self.splice_chunk_size[self.chunk_idx]

        filename = f"encrypts/{self.chunk_idx}.rsb" if is_encryption else "decrypts/gigabyte.bin"
        self.write_buffer = open(filename, "wb")


    def process_chunk(self, data, eof = False):
        data_coordinates = 0  # 현재 파일에서의 처리 현황 [ = 현재 cursor 위치 ]
        while True:
            while self.accumulated_bytes < self.current_chunk_size:
                # 현재 1MB 조각에 아직 읽을 데이터가 충분히 남아 있을 때 [ left_data_to_read > insufficient_chunk_data_size ]
                if len(data) - data_coordinates > self.current_chunk_size - self.accumulated_bytes:
                    to_write = data[data_coordinates : data_coordinates + self.current_chunk_size - self.accumulated_bytes]
                    self.write_buffer.write(to_write)
                    data_coordinates += self.current_chunk_size - self.accumulated_bytes
                    self.accumulated_bytes += self.current_chunk_size - self.accumulated_bytes
                else:
                    to_write = data[data_coordinates:]
                    self.write_buffer.write(to_write)
                    self.accumulated_bytes += len(data) - data_coordinates

                    if self.is_encryption and eof:
                        self.write_buffer.close()
                        upload_file(self.write_buffer.name)
                    return
            
            self.accumulated_bytes = 0  # 바이트 수 초기화
            if (self.chunk_idx + 1 != len(self.splice_chunk_size)):
                self.chunk_idx += 1
                self.current_chunk_size = self.splice_chunk_size[self.chunk_idx]
            
            if self.is_encryption:
                self.write_buffer.close()
                upload_file(self.write_buffer.name)  # 파일 업로드
                self.write_buffer = open(f"encrypts/{self.chunk_idx}.rsb", "wb")
