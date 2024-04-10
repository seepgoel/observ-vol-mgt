import configargparse

configuration = None


def get_configuration():
    return configuration


def parse_configuration():
    p = configargparse.ArgParser(
        default_config_files=['~/controller.config.yaml', 'config.yaml'])
    p.add('-c', '--config-file', required=False,
          is_config_file=True, help='config file path')
    p.add('-v', '--loglevel', help='logging level',
          default='info', env_var='LOGLEVEL')
    p.add('--ingest_type', help='ingest type (dummy, file or promql)',
          default='dummy', env_var='INGEST_TYPE')
    p.add('--ingest_file', help='ingest file ( for file type )',
          env_var='INGEST_FILE')
    p.add('--ingest_url', help='ingest url ( for promql type )',
          env_var='INGEST_URL')
    p.add('--ingest_window', help='ingest window ( for promql type )',
          env_var='INGEST_WINDOW')

    global configuration
    configuration = p.parse_args()
    print(configuration)
    print("----------")
    print(p.format_help())
    print("----------")
    print(p.format_values())