# -*- coding: utf-8 -*-

import json
import random
import datetime
import tempfile
import zipfile
import shutil
import boto3

ferry_list = ["gabriella","mariella","seppo","nir","pixel","airplane","toy","ascii","bus","surreal","tardis"]
audio_list = ["2006_original","2018_remake","acapella_01","bells_01","metal_01","metal_02","piano_01","piano_02","synth_01","synth_02","synth_03","synth_04","synth_05","neofarjan","tidsmaskinen","spooky"]
bg_list = ["none","ground","pixel","waves","sunset","party","sky","seagul","diagram","hull","ship"]
fg_list = ["none","waves","land","party"]
sun_list = ["sun","sun_toon","sun_pixel"]
font_list = ["arial_bold","comic_sans_bold"]

def random_pick(some_list):
    return random.SystemRandom().choice(some_list)

def get_file(name_list, prefix, suffix):
    return prefix + random_pick(name_list) + suffix

def get_length():
    return 60.0 + random_pick([0,0,0,0,0,10,20,30])

def get_demo_title():
    return "{}{}{}{}{}".format(
        random_pick(['the ','']),
        random_pick(['maybe ', 'first ','only ','']),
        random_pick(['beatable ','surreal ','successful ','superb ','excellent ','superior ', 'incredible ','second ','first ','only ','Jumalauta ','JML ','']),
        random_pick(['submarine','färjan','finlandsfärjan','ålandsfärjan','sverigesfärjan','dead horse','ferry','means to travel','vehicle','Gabriella','Mariella','Seppo','waste of time and resources']),
        random_pick(['!','?','.']))

def get_greets():
    groups = ['Äärikeskusta','Jumalauta','iSO','Leipaeae','penishure','Spacepigs','Schnappsgirls','Fiture crew','Lamers','Jukupliut','ekspert','oSI','ASD','asddsa','Fairlight','Yleisradio','Ninja Gefilus','Saksalainen laatu','HiRMU','Poo-brain','HODOR','TGD','FIRG','Gerbil']
    random.SystemRandom().shuffle(groups)
    group_str = ""
    for i in range(0, random_pick([1,2,3,4,5,6])):
        group_str = group_str + ", " + groups.pop()
    group_str = group_str[2:] + " and " + groups.pop() + "..."
    return "Greetings to {}".format(group_str)

def get_current_date():
    return datetime.datetime.today().strftime(random_pick(['%Y-%m-%d','%d.%m.%Y','%m/%d/%Y','%Y/%m/%d']))

def get_sentence():
    if random_pick([1,2,3,4]) == 1:
        return ""

    return " {}{} {}{}{}{}{}".format(random_pick(['Yesterday ','On Tuesday ','Last Jumalauta party ','At Boozembly ','Last week ','A moment ago ','Last month ','Last year ','In the begin ']),
        random_pick(['I','you','we','those lamers','Äärikeskusta','Jumalauta','iSO','Leipaeae','penishure','Spacepigs','Schnappsgirls','Fiture crew','Lamers','Jukupliut','ekspert','oSI','ASD','asddsa','Fairlight','Yleisradio','Ninja Gefilus','Saksalainen laatu','HiRMU','Poo-brain','HODOR','TGD','FIRG','Gerbil']),
        random_pick(['had ','had not ']),
        random_pick(['an epiphany ','understood ','understanding ','understated ','a demo ','an intro ','a compo entry ']),
        random_pick(['about ','regarding ','your ']),
        random_pick(['the eating contest','a demoparty','playing cards against humanity','random habits','finlandsfärjan','färjan','ferry','furries']),
        random_pick(['!','.']))

def get_scroller():
    return "Jumalauta Färjan {}: {} {}{}".format(get_current_date(), get_demo_title(), get_greets(), get_sentence())

def create_demo():
    demo_length = get_length()

    data = {
        "custom": {
            "farjan": {
                "background": {
                    "angle": {
                        "v": "{\"degreesZ\":\"{return Math.sin(getSceneTimeFromStart())*"+random_pick(['2-1','0'])+";}\"}"
                    },
                    "position": {
                        "v": "{\"x\":\"{return getScreenWidth()/2.0+Math.sin(getSceneTimeFromStart())*"+random_pick(['0','5','10','15','8','7','0','0'])+";}\",\"y\":\"{ return getScreenHeight()/2.0;}\"}"
                    },
                    "scale": {
                        "v": "{\"uniform2d\":1."+random_pick(['1','125','15','2'])+"}"
                    }
                },
                "ferry": {
                    "angle": {
                        "v": "{\"degreesZ\":\"{return Math.sin(getSceneTimeFromStart())*"+random_pick(['2-1','0','4-2','6-3'])+";}\"}"
                    },
                    "position": {
                        "v": "{\"x\":-700,\"y\":"+random_pick(['700','650','600'])+"},{\"duration\":"+str(demo_length)+", \"x\":2500,\"y\":"+random_pick(['700','650','600','500','550','450'])+"}"
                    },
                    "scale": {
                        "v": ""
                    }
                },
                "font": {
                    "angle": {
                        "v": ""
                    },
                    "color": {
                        "v": "{\"r\":255,\"g\":255,\"b\":255,\"a\":200}"
                    },
                    "position": {
                        "v": "{\"x\":\"{return Settings.demo.custom.farjan.scroller.v.length*200+getScreenWidth();}\",\"y\":\"{ return getScreenHeight()/2+100;}\"},{\"duration\":"+str(demo_length)+",\"x\":\"{return -(Settings.demo.custom.farjan.scroller.v.length*200+getScreenWidth());}\",\"y\":\"{ return getScreenHeight()/2-400;}\"}"
                    },
                    "scale": {
                        "v": "{\"x\":20,\"y\":20}"
                    }
                },
                "foreground": {
                    "angle": {
                        "v": "{\"degreesZ\":\"{return Math.sin(getSceneTimeFromStart())*"+random_pick(['2-1','0'])+";}\"}"
                    },
                    "position": {
                        "v": ""
                    },
                    "scale": {
                        "v": "{\"uniform2d\":1."+random_pick(['1','125','15','2'])+"}"
                    }
                },
                "release": {
                    "v": True
                },
                "scroller": {
                    "v": get_scroller()
                },
                "sun": {
                    "shadow": {
                        "v": random_pick([True,False,True,True,True])
                    }
                }
            },
            "background": get_file(bg_list, "background/background_", ".png"),
            "ferry": get_file(ferry_list, "ferry/boat_", ".png"),
            "font": get_file(font_list, "font/", ".ttf"),
            "foreground": get_file(fg_list, "foreground/foreground_", ".png"),
            "sun": get_file(sun_list, "sun/", ".png")
        },
        "length": demo_length,
        "song": get_file(audio_list, "audio/farjan_", ".ogg"),
        "songLoop": True,
        "title": "Färjanmaker"
    }

    try:
        script_file_path = "/tmp/script.json"
        demo_script = open(script_file_path,"w") 
        demo_script.write(json.dumps(data)) 
        demo_script.close() 

        bucket = 'jml-daily-farjan-metadata'
        key = "scripts/{}/script.json".format(datetime.datetime.today().strftime('%Y/%m/%d'))
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(script_file_path, bucket, key)

        return key
    except Exception as e:
        print(e)
        raise e

def lambda_handler(event, context):
    key = create_demo()
    
    return {
        "statusCode": 200,
        "body": json.dumps({'key':key})
    }

