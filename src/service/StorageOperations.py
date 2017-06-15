#!/usr/bin/env python

from swiftclient.multithreading import OutputManager
from swiftclient.service import SwiftError, SwiftService, SwiftUploadObject

#Logging
import logging
logging.basicConfig(level=logging.ERROR)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("swiftclient").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

_opts = {'object_uu_threads': 20}
def upload_file(file,filename,container):
    print(file)
    with SwiftService(options=_opts) as swift, OutputManager() as out_manager:
        try:
            objs = []
            objs.append(SwiftUploadObject(file, object_name=filename))

            # Schedule an upload to swift
            for r in swift.upload(objects=objs, container=container):
               if r['success']:
                  if 'object' in r:
                     print(r['object'])
                  elif 'for_object' in r:
                     print('%s segment %s' % (r['for_object'], r['segment_index']))
               else:
                  error = r['error']
                  logger.error( "Failed to upload object to container")
               print r

        except SwiftError as e:
            logger.error(e.value)


def download_file(filename,container,downloadFolder=None):
    opts = {'out_directory': downloadFolder}
    with SwiftService() as swift:
        try:
            down_res = swift.download(container=container,objects=[filename],options=opts).next()
            if down_res['success']:
                print("'%s' downloaded" % down_res['object'])
                return down_res['path']
            else:
                print("'%s' download failed" % down_res['object'])
        except SwiftError as e:
            logger.error(e.value)
    return None

def file_exists(filename,container):
	with SwiftService(options=_opts) as swift:
		stats_it = swift.stat(container=container, objects=[filename])
		stat_res = stats_it.next()
		if stat_res['success']:
			return True
		else:
                        return False


def delete_file(filename, container):
    objects = [filename]
    with SwiftService(options=_opts) as swift:
        del_iter = swift.delete(container=container, objects=objects)
        for del_res in del_iter:
            c = del_res.get('container', '')
            o = del_res.get('object', '')
            a = del_res.get('attempts')
            if del_res['success'] and not del_res['action'] == 'bulk_delete':
                rd = del_res.get('response_dict')
                if rd is not None:
                    t = dict(rd.get('headers', {}))
                    if t:
                        print('Successfully deleted {0}/{1} in {2} attempts (transaction id: {3})'.format(c, o, a, t))
                    else:
                        print('Successfully deleted {0}/{1} in {2} attempts'.format(c, o, a))
