from src.common.processors.base_processor import FFmpegProcessor
from src.core.datacls import FFmpegDTO


class GeneratorFFmpegCommandProcessor(FFmpegProcessor):
    def process(self, data: list[FFmpegDTO]) -> list[FFmpegDTO]:


        return data
