from setuptools import setup, find_packages

setup(
    name='fomars-kafka-exercise',
    version=0.1,
    python_requires='==3.7.*',
    packages=find_packages(),
    # namespace_packages=["fomars_kafka_exercise"],
    install_requires=[
        'certifi==2020.11.8',
        'chardet==3.0.4',
        'idna==2.10',
        'kafka-python==2.0.2',
        'psycopg2-binary==2.8.6',
        'requests==2.25.0',
        'urllib3==1.26.2'
    ],
    entry_points={
        'console_scripts': [
            'fomars-kafka-producer = fomars_kafka_exercise.producer:main',
            'fomars-kafka-consumer = fomars_kafka_exercise.consumer:main',
        ]}
)
