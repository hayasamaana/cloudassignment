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
    with SwiftService(options=_opts) as swift, OutputManager() as out_manager:
        try:
            objs = []
            objs.append(SwiftUploadObject(file, object_name=filename))

            # Schedule uploads on the SwiftService thread pool and iterate
            # over the results
            for r in swift.upload(container, objs):
                if r['success']:
                    if 'object' in r:
                        print(r['object'])
                    elif 'for_object' in r:
                        print(
                            '%s segment %s' % (r['for_object'],
                                               r['segment_index'])
                            )
                else:
                    error = r['error']
                    if r['action'] == "create_container":
                        logger.warning(
                            'Warning: failed to create container '
                            "'%s'%s", container, error
                        )
                    elif r['action'] == "upload_object":
                        logger.error(
                            "Failed to upload object %s to container %s: %s" %
                            (container, r['object'], error)
                        )
                    else:
                        logger.error("%s" % error)
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
