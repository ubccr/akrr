# CLI for performance monitoring routines

def add_command_ingestor(parent_parser):
    """
    Ingestion to XDMoD
    """
    parser = parent_parser.add_parser('ingestor', description=add_command_ingestor.__doc__)
    subparsers = parser.add_subparsers(title='commands')

    cli_ingestor_single_task(subparsers)


def cli_ingestor_single_task(parent_parser):
    """
    Ingest single task
    """
    parser = parent_parser.add_parser('single-task', description=cli_ingestor_single_task.__doc__)
    parser.add_argument('task_id', metavar='task-id', type=int, help='task id of task to ingest')

    def handler(args):
        from akrr.perf.ingestor import ingest_single_task
        return ingest_single_task(args.task_id)

    parser.set_defaults(func=handler)