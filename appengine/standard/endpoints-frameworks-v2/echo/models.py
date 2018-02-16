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


class Task(ndb.Model):
    tag = ndb.KeyProperty(kind=Tag)
    start = ndb.DateTimeProperty(auto_now_add=True)
    end = ndb.DateTimeProperty(auto_now=True)
    email = ndb.StringProperty()
    last_id = ndb.StringProperty(default='0')
    counting = ndb.IntegerProperty(default=0)


class Forum(ndb.Model):
    forum = ndb.StringProperty(required=True)
    url = ndb.StringProperty(indexed=False)

    @property
    def tasks(self):
        return Task.query(Task.forum == self.key)

    @property
    def topics(self):
        return Topic.gql("WHERE tags = :1", self.key)
