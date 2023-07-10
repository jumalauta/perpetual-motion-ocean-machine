'use strict';

var AWS = require('aws-sdk');

var METADATA_BUCKET = 'jml-daily-farjan-metadata';
var OUTPUT_BUCKET = 'jml-daily-farjan-output';

function getFarjanOutputKey(date) {
    return "output/jumalauta-farjan-" + String(date) + ".zip";    
}

function getFarjan(date, done) {
    var s3 = new AWS.S3();

    var fileKey = getFarjanOutputKey(date);

    var params = {
        Bucket: OUTPUT_BUCKET,
        Prefix: fileKey,
        MaxKeys: 1
    };
    s3.listObjects(params, function(err, data) {
        if (err) {
            console.log(err, err.stack);
        }

        if (data && data.Contents && data.Contents.length > 0 && data.Contents[0].Key === fileKey) {
            console.log("Cached farjan found: " + date);
            // File is cached in the output
            done(null, {"url": fileKey});
        } else {
            console.log("Farjan not found with fileKey: " + fileKey + ", data: " + JSON.stringify(data));

            generateFarjan(date, done);
        }
    });
}

function generateFarjan(date, done) {
    var s3 = new AWS.S3();

    var dateSplit = date.split("-");

    var scriptKey = "scripts/"+dateSplit[0]+"/"+dateSplit[1]+"/"+dateSplit[2]+"/script.json";

    var params = {
        Bucket: METADATA_BUCKET,
        Prefix: scriptKey,
        MaxKeys: 1
    };
    s3.listObjects(params, function(err, data) {
        if (err) {
            console.log(err, err.stack);
        }

        // Is source data for date available?
        if (data && data.Contents && data.Contents.length > 0 && data.Contents[0].Key === scriptKey) {
            console.log("Generating new farjan from: " + scriptKey);

            // Generate farjan!
            var lambda = new AWS.Lambda();
            var params = {
                FunctionName: "JmlDailyFarjanPackager",
                InvocationType: "RequestResponse",
                Payload: new Buffer(JSON.stringify({'scriptKey': scriptKey}), 'utf8')
            };


            // URL: https://docs.aws.amazon.com/AWSJavaScriptSDK/latest/AWS/Lambda.html#invoke-property
            lambda.invoke(params, function(err, data) {
                if (err) {
                    console.log(err, err.stack);
                    done(new Error("Cannot generate farjan: " + date));
                } else {
                    console.log("Farjan generated: " + date);
                    done(null, {"url": getFarjanOutputKey(date)});
                }
            });
        } else {
            console.log("Farjan not found with scriptKey: " + scriptKey + ", data: " + JSON.stringify(data));
            done(new Error("Farjan not found: " + date));
        }
    });
}

/**
 * Give download link to farjan or generate farjan on-the-fly
 */
exports.handler = (event, context, callback) => {
    const done = (err, res) => callback(null, {
        statusCode: err ? '400' : '200',
        body: err ? JSON.stringify({"url":"error.html", "message":err.message}) : JSON.stringify(res),
        headers: {
            'Content-Type': 'application/json',
        },
    });

    console.log("Farjan download requested. event: " + JSON.stringify(event));

    var date = event["farjanDate"];

    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        console.log("bad event: " + JSON.stringify(event));
        done(new Error("Invalid date"));
        return;
    }

    getFarjan(date, done);
};
