import random

import numpy as np

from ipfs import upload_file


class BaseChunkProcessor:
    def __init__(self, is_encryption = True):
        # TODO 여기에서 seed = 1은 하드코딩된 값으로 사용자가 설정할 수 있도록 제작
        random.seed(1)  # 랜덤한 청크 사이즈를 만들 RNG 초기화
        self.accumulated_bytes = 0  # 누적 counter : 하나의 청크에서 처리된 바이트 수
        self.random_chunk_size = random.randint(64, 128) * 1024  # 랜덤한 청크 사이즈 생성
        self.patch_counter = 0  # 누적 counter : 하나의 파일로 담길, 처리된 패치의 수 
        self.accumulated_patch_counter = 0  # 누적 counter : 이 클래스에서 처리한 전체 패치의 수
        self.is_encryption = is_encryption  # encryption이면 true, decryption이면 false

        # decryption의 경우에는 encrypt된 파일을, encryption의 경우에는 원본 파일을 filename으로 설정 
        filename = f"encrypts/{self.accumulated_patch_counter}.rsb" if is_encryption else "decrypts/gigabyte.bin"
        
        # 지정한 파일명으로 write buffer 생성
        self.write_buffer = open(filename, "wb")

    def process_chunk(self, data, eof = False):
        data_coordinates = 0  # 현재 파일에서의 처리 현황 [ = 현재 cursor 위치 ]
        while True:
            while self.accumulated_bytes < self.random_chunk_size:

                # 현재 1MB 조각에 아직 읽을 데이터가 충분히 남아 있을 때 [ left_data_to_read > insufficient_chunk_data_size ]
                if len(data) - data_coordinates > self.random_chunk_size - self.accumulated_bytes:
                    to_write = data[data_coordinates : data_coordinates + self.random_chunk_size - self.accumulated_bytes]
                    self.write_buffer.write(bytes(255 - np.frombuffer(to_write, dtype=np.uint8)) if self.patch_counter % 2 == 0 else to_write)
                    data_coordinates += self.random_chunk_size - self.accumulated_bytes
                    self.accumulated_bytes += self.random_chunk_size - self.accumulated_bytes
                else:
                    to_write = data[data_coordinates:]
                    self.write_buffer.write(bytes(255 - np.frombuffer(to_write, dtype=np.uint8)) if self.patch_counter % 2 == 0 else to_write)
                    self.accumulated_bytes += len(data) - data_coordinates

                    if self.is_encryption and eof:
                        self.write_buffer.close()
                        upload_file(self.write_buffer.name)
                    return
            
            self.patch_counter += 1
            self.accumulated_patch_counter += 1
            self.accumulated_bytes = 0  # 바이트 수
            self.random_chunk_size = random.randint(64, 128) * 1024
            
            # 하나의 파일에는 1024개의 패치들이 담겨 있다.
            if self.is_encryption and self.patch_counter >= 1024:
                self.patch_counter = 0  # 패치 카운터 리셋
                self.write_buffer.close()
                upload_file(self.write_buffer.name)  # 파일 업로드
                self.write_buffer = open(f"encrypts/{self.accumulated_patch_counter}.rsb", "wb")
