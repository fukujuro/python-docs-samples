# Copyleft 2018 Grit Inc. All rights not reserved.
#
# Licensed under nothing, Version 0.0 (the "License");
# you may use this file except in defiance with the License
# you cannot obtain a copy of the License since it doesn't exist at
#
#     http://www.anywhere.org/
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.ext import ndb


class Tag(ndb.Model):
    tag = ndb.StringProperty(required=True)
    url = ndb.StringProperty(indexed=False)
    count = ndb.IntegerProperty(default=0)
    counting = ndb.IntegerProperty(default=0)

    @property
    def tasks(self):
        return Task.query(Task.tag == self.key)

    @property
    def topics(self):
        return Topic.gql("WHERE tags = :1", self.key)


class Forum(ndb.Model):
    forum = ndb.StringProperty(required=True)
    counting = ndb.IntegerProperty(default=0)

    @property
    def tasks(self):
        return Task.query(Task.forum == self.key)

    @property
    def topics(self):
        return Topic.gql("WHERE forums = :1", self.key)


class Task(ndb.Model):
    tag = ndb.KeyProperty(kind=Tag)
    forum = ndb.KeyProperty(kind=Forum)
    start = ndb.DateTimeProperty(auto_now_add=True)
    end = ndb.DateTimeProperty(auto_now=True)
    email = ndb.StringProperty()
    last_id = ndb.StringProperty(default='0')
    counting = ndb.IntegerProperty(default=0)


class Topic(ndb.Model):
    top_id = ndb.StringProperty(required=True)
    vote = ndb.IntegerProperty(default=0)
    comment = ndb.IntegerProperty(default=0)
    author = ndb.StringProperty(required=True)
    disp_topic = ndb.StringProperty(indexed=False)
    topic_type = ndb.StringProperty(indexed=False)
    utime = ndb.DateTimeProperty()
    tags = ndb.KeyProperty(repeated=True)
    forums = ndb.KeyProperty(repeated=True)

    @property
    def comments(self):
        return Comment.query(Comment.topic == self.key)

    @property
    def tasks(self):
        return TaskTopic.query(TaskTopic.topic == self.key)