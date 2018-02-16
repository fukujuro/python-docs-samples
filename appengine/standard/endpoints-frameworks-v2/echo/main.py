# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is a sample Hello World API implemented using Google Cloud
Endpoints."""

# [START imports]
import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

import webapp2
import requests
from requests_toolbelt.adapters import appengine
import json
from models import Task
from models import Forum
from models import topic
from datetime import datetime
from google.appengine.ext import ndb
# [END imports]

appengine.monkeypatch()

# [START messages]
class EchoRequest(messages.Message):
    content = messages.StringField(1)

class EchoResponse(messages.Message):
    """A proto Message that contains a simple string field."""
    content = messages.StringField(1)

class TaskForm(messages.Message):
    forum = messages.StringField(1)
    loops = messages.IntegerField(2, default=1)

ECHO_RESOURCE = endpoints.ResourceContainer(
    EchoRequest,
    n=messages.IntegerField(2, default=1))
# [END messages]


# [START echo_api]
@endpoints.api(name='echo', version='v1')
class EchoApi(remote.Service):

    @endpoints.method(TaskForm, TaskForm, path='forum',
        http_method='POST', name='forum')
    def forum(self, request):
        forum_key = ndb.Key(Forum, request.forum)
        forum = Forum.get_or_insert(request.forum,
                                    key = forum_key),
                                    forum = request.forum)
        task_id = Task.allocate_ids(size=1)[0]
        task_key = ndb.Key(Task, task_id)
        task = Task(key = task_key,
                    forum = forum_key)
        taskqueue.add(params={'forum'   : request.forum,
                              'loops'    : request.loops,
                              'task_key': task.key.urlsafe()},
                      url='/collect_topics/forums/')
        task.put_async()
        return TaskForm(forum=request.forum)


    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        ECHO_RESOURCE,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/{n}',
        http_method='POST',
        name='echo_path_parameter')
    def echo_path_parameter(self, request):
        output_content = ' '.join([request.content] * request.n)
        return EchoResponse(content=output_content)

    @endpoints.method(
        # This method takes a ResourceContainer defined above.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/getApiKey',
        http_method='GET',
        name='echo_api_key')
    def echo_api_key(self, request):
        return EchoResponse(content=request.get_unrecognized_field_info('key'))

    @endpoints.method(
        # This method takes an empty request body.
        message_types.VoidMessage,
        # This method returns an Echo message.
        EchoResponse,
        path='echo/getUserEmail',
        http_method='GET',
        # Require auth tokens to have the following scopes to access this API.
        scopes=[endpoints.EMAIL_SCOPE],
        # OAuth2 audiences allowed in incoming tokens.
        audiences=['your-oauth-client-id.com'])
    def get_user_email(self, request):
        user = endpoints.get_current_user()
        # If there's no user defined, the request was unauthenticated, so we
        # raise 401 Unauthorized.
        if not user:
            raise endpoints.UnauthorizedException
        return EchoResponse(content=user.email())
# [END echo_api]


# [START api_server]
api = endpoints.api_server([EchoApi])
# [END api_server]


class CollectTopicsForumHandler(webapp2.RequestHandler):

    def post(self):
        forum = self.request.get('forum')
        urlsafe = self.request.get('task_key')
        loops = self.request.get('loops')
        task_key = ndb.Key(urlsafe=urlsafe)
        task = task_key.get()
        task_id = str(task_key.id())

        # counting = task.counting
        
        url = 'https://pantip.com/forum/topic/ajax_json_all_topic_tag'
        headers = { 'User-Agent': 'grit.intelligence@gmail.com',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'x-requested-with': 'XMLHttpRequest'}
        payload = [ ('last_id_current_page', '0'),
                    ('dataSend[forum]', forum),
                    ('dataSend[topic_type][type]', '0'),
                    ('dataSend[topic_type][default_type]', '1'),
                    ('thumbnailview', 'false'),
                    ('current_page', '1')]
        if task.last_id != '0':
            payload[0] = (payload[0][0], task.last_id)
        res = requests.post(url, payload, headers=headers)
        j = res.json()
        item = j['item']
        looping = 0
        while len(item['topic']) > 0 and looping < loops:
            for t in item['topic']:
                if '_id' not in t.keys():
                    continue
                tags = []
                if isinstance(t['tags'], list):
                    for tt in t['tags']:
                        tags.append(ndb.Key(Tag, tt['tag']))
                forums = []
                forums.append(ndb.Key(Forum, forum))
                top_key = ndb.Key(Topic, str(t['_id']))
                topic = Topic(key = top_key,
                              top_id = str(t['_id']),
                              vote = t['votes'],
                              comment = t['comments'],
                              author = t['author'],
                              disp_topic = t['disp_topic'],
                              topic_type = str(t['topic_type']),
                              utime = datetime.strptime(t['utime'], '%m/%d/%Y %H:%M:%S'),
                              tags = tags,
                              forums = forums)
                topics.append(topic)
                counting += 1
            ndb.put_multi_async(topics)
            task.last_id = str(item['last_id_current_page'])
            task.counting = counting
            task.put_async()
            looping += 1
            payload[0] = (payload[0][0], task.last_id)
            res = requests.post(url, payload, headers=headers)
            j = res.json()
            item = j['item']


app = ndb.toplevel(
    webapp2.WSGIApplication([
    ('/collect_topics/forum', CollectTopicsForumHandler)
    ],
    debug=True)
)