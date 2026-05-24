"""EKP - 企业级知识中台命令行工具"""

import click
from pathlib import Path
from .core.platform import KnowledgePlatform


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """EKP - Enterprise Knowledge Platform, 企业级知识中台"""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--sheet-name", "-s", help="Excel 文件的表名")
def info(file_path: str, sheet_name: str):
    """查看表格文件信息"""
    try:
        ekp = KnowledgePlatform()
        df = ekp.load_table(file_path, sheet_name)
        metadata = ekp.metadata[Path(file_path).name]

        click.echo(f"📊 表格信息: {Path(file_path).name}")
        click.echo(f"行数: {metadata['rows']}")
        click.echo(f"列数: {len(metadata['columns'])}")
        click.echo("\n列信息:")
        for col, dtype in metadata['dtypes'].items():
            null_count = metadata['null_values'][col]
            click.echo(f"  - {col} ({dtype}, 空值: {null_count})")

    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}", err=True)


@cli.command()
@click.argument("question")
@click.option("--datasource", "-d", help="指定查询的数据源")
def query(question: str, datasource: str):
    """自然语言查询知识中台"""
    try:
        ekp = KnowledgePlatform()
        result = ekp.query(question, datasource)
        click.echo(result)
    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}", err=True)


@cli.command(name="list")
def list_datasources():
    """列出所有已接入的数据源"""
    try:
        ekp = KnowledgePlatform()
        summary = ekp.get_datasource_summary()
        click.echo(f"📚 已接入数据源总数: {summary['total_datasources']}")
        for name, info in summary['datasources'].items():
            click.echo(f"  - {name} ({info['type']}): {info['status']}")
    except Exception as e:
        click.echo(f"❌ 错误: {str(e)}", err=True)


if __name__ == "__main__":
    cli()
