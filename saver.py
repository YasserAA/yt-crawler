# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import errorcode
from slugify import slugify
import requests
import pprint
import os
pp = pprint.PrettyPrinter(indent=4)


class Saver(object):
    # Connect to mysql server
    def __enter__(self):
        self.cursor = None
        try:
            self.cnx = mysql.connector.connect(user='root',
                                               password="12345678",
                                               host='localhost', port='3306',
                                               database='ytcrawler')
            self.cnx.autocommit = True
            self.cursor = self.cnx.cursor()
            print 'Connected to DB...'
        except mysql.connector.Error as err:
            print "WTF"
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            return self

    def __exit__(self, type, value, traceback):
        try:
            self.cnx.close()
        except AttributeError:
            pass

    # Creates a path if it doesn't exist
    def check_path(self, path):
        try:
            os.makedirs(path)
        except OSError:
            pass

    # Save thumb image
    def save_thumb(self, file_name, link, kind):
        try:
            response = requests.get(link, stream=True)
        except requests.exceptions.ConnectionError:
            return ''
        
        if response.status_code == 200:
            path = "./images/%s/" % kind
            self.check_path(path)

            with open(path + file_name, 'w') as image_file:
                image_file.write(response.content)
                return os.path.realpath(image_file.name)
        else:
            print "An error occured during fetching %s" % link
        return ''

    # Save data to DB
    def save_db(self, video_id, video_data):
        if video_data.get('saved'):
            return
        elif self.cursor:
            print "\n------------------- Saving %s ---------------" % video_data['name'].encode('utf-8')
            # pp.pprint(video_data)
            video_data['saved'] = True

            insert_cmd = """INSERT INTO video VALUES ("{0}", "{1}", "{2}", "{3}",
                                                        "{4}", "{5}", "{6}", "{7}", "{8}")
            ON DUPLICATE KEY UPDATE title="{1}", views="{2}" """.format(
                video_id,
                video_data['name'],
                video_data['views'],
                video_data['duration'],
                video_data['video_url'],
                video_data['thumb_link'],
                video_data['thumb_path'].encode('utf-8'),
                video_data['full_thumb_link'].encode('utf-8'),
                video_data['full_thumb_path'].encode('utf-8'),
            )
            try:
                self.cursor.execute(insert_cmd)
            except mysql.connector.Error as err:
                print insert_cmd
                print err
        else:
            return
            print "------------------- Saving %s ---------------" % video_data['name'].encode('utf-8')
            pp.pprint(video_data)

    # Save video image and data
    def save(self, videos):
        for video_id, video_data in videos.iteritems():

            file_name = slugify(video_data['name']) + '.jpg'
            if not video_data.get('thumb_path'):
                try:
                    video_data['thumb_path'] = self.save_thumb(file_name, video_data['thumb_link'], 'thumb')

                    video_data['full_thumb_path'] = self.save_thumb(file_name, video_data['full_thumb_link'],
                                                                    'full_thumb')
                except ValueError:
                    print "Could not save thumb image"
            self.save_db(video_id, video_data)
