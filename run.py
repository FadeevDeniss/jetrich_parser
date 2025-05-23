import time, signal

from dotenv import load_dotenv
from cli import CliParser
from conf import Settings
from jetrich_parser import JetrichParser
from tasks import parsing_task, sig_handler, ProgramKilled, ParsingTask


HEADERS: dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                  ' (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
              'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}


def main(interval: int, parser):
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    task = ParsingTask(interval, parsing_task, parser)
    task.start()

    while True:
        try:
            time.sleep(1)
        except ProgramKilled:
            task.stop()
            break


if __name__ == '__main__':
    load_dotenv(Settings.BASE_DIR)
    cli_arguments = CliParser('jetrich_parser').get_interval()
    main(cli_arguments, JetrichParser(Settings, HEADERS))
