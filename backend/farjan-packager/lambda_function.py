# -*- coding: utf-8 -*-

import json
import tempfile
import zipfile
import shutil
import boto3

def package_demo(s3_script_key):
    s3 = boto3.resource('s3')

    # figure out the date from input script file
    # s3_script_key = "scripts/2018/09/12/script.json"
    s3_script_key_split = s3_script_key.split('/')
    current_day = "{}-{}-{}".format(s3_script_key_split[1], s3_script_key_split[2], s3_script_key_split[3])
    
    # create temporary directory
    temp_dir = tempfile.mkdtemp(suffix=current_day, prefix='farjan', dir='/tmp')

    # Download S3 source zip thing and metadata to the temp directory

    zip_path = "{}/jumalauta-farjan.zip".format(temp_dir)
    script_path = "{}/script.json".format(temp_dir)

    source_bucket = 'jml-daily-farjan-metadata'
    destination_bucket = 'jml-daily-farjan-output'
    s3.meta.client.download_file(source_bucket, 'src/jumalauta-farjan.zip', zip_path)
    s3.meta.client.download_file(source_bucket, s3_script_key, script_path)

    # Extract source farjan
    source_farjan_zip = zipfile.ZipFile(zip_path, 'r')
    source_farjan_zip.extractall(temp_dir)
    source_farjan_zip.close()

    # Rename the demo folder to use current date
    demo_base_folder = "jumalauta-farjan-{}".format(current_day)
    shutil.move("{}/jumalauta-farjan".format(temp_dir), "{}/{}".format(temp_dir, demo_base_folder))

    # read script
    with open(script_path) as script_file:
        script = json.load(script_file)
    
    # add required datas to the package data directory
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['song']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['song']))
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['custom']['foreground']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['custom']['foreground']))
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['custom']['background']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['custom']['background']))
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['custom']['sun']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['custom']['sun']))
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['custom']['ferry']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['custom']['ferry']))
    s3.meta.client.download_file(source_bucket, "src/data/{}".format(script['custom']['font']), "{}/{}/data/{}".format(temp_dir, demo_base_folder, script['custom']['font']))

    # Add the script metadata to farjan package data directory
    shutil.move(script_path, "{}/{}/data/script.json".format(temp_dir, demo_base_folder))

    # Write new farjan to zip
    file_format = "zip"
    file_archive_base_name = "{}/{}".format(temp_dir, demo_base_folder)
    shutil.make_archive(file_archive_base_name, file_format, temp_dir, demo_base_folder)

    # Put to S3
    key = "output/{}.{}".format(demo_base_folder, file_format)
    s3.meta.client.upload_file("{}.{}".format(file_archive_base_name, file_format), destination_bucket, key)

    # Remove temp directory
    shutil.rmtree(temp_dir)
    
    return key

def lambda_handler(event, context):
    key = None
    if event:
        # S3 new file trigger
        if 'Records' in event:
            for record in event['Records']:
                if record.get('eventSource',None) == 'aws:s3':
                    s3_key = record['s3']['object']['key']
                    key = package_demo(s3_key)
        # User manual download trigger (if färjan has already been cleaned)
        elif 'scriptKey' in event:
            s3_key = event['scriptKey']
            key = package_demo(s3_key)

    if key != None:
        return {
            "statusCode": 200,
            "body": json.dumps({'key': key})
        }
    else:
        return {
            "statusCode": 400
        }
