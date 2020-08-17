from boto3 import resource as boto3resource
from dagster import pipeline, solid, Output, OutputDefinition, InputDefinition, \
    ModeDefinition, default_executors, default_intermediate_storage_defs, resource, \
    Field
from dagster_aws.s3 import s3_intermediate_storage
from dagster_celery import celery_executor


# The minio_resource was copied and adapted from s3_resource because s3_resource does not support
# specifying access keys.
@resource({
    'endpoint_url': Field(
        str, description='Endpoint where the Minio API can be reached', is_required=True
    ),
    'access_key': Field(
        str, description='Access key (credentials)', is_required=True
    ),
    'secret_key': Field(
        str, description='Secret key (credentials)', is_required=True
    )
})
def minio_resource(context):
    endpoint_url = context.resource_config.get('endpoint_url')
    access_key = context.resource_config.get('access_key')
    secret_key = context.resource_config.get('secret_key')

    return boto3resource(
        's3',
        use_ssl=True,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    ).meta.client


@solid(
    input_defs=[InputDefinition('in1', str)],
    output_defs=[OutputDefinition(name="out1", dagster_type=str)]
)
def basic_solid(context, in1):
    context.log.info('Running basic_solid for "{}"'.format(in1))
    yield Output('basic_solid({})'.format(in1), output_name='out1')


@solid(
    input_defs=[InputDefinition('in1', str)],
    output_defs=[OutputDefinition(name="out1", dagster_type=str)],
    tags={'dagster-celery/queue': 'gpu'}
)
def gpu_solid(context, in1):
    context.log.info('Running gpu_solid for "{}"'.format(in1))
    yield Output('gpu_solid({})'.format(in1), output_name='out1')


mode_definitions = [
    ModeDefinition(
        executor_defs=default_executors + [celery_executor],
        intermediate_storage_defs=default_intermediate_storage_defs + [s3_intermediate_storage],
        resource_defs={'s3': minio_resource})
]


@pipeline(mode_defs=mode_definitions)
def the_pipeline():
    r1 = basic_solid()
    gpu_solid(r1)


