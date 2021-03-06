# Copyright (c) 2018 RedHat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from kuryr_kubernetes.handlers import k8s_base


class TestHandler(k8s_base.ResourceEventHandler):

    OBJECT_KIND = 'DUMMY'
    OBJECT_WATCH_PATH = 'DUMMY_PATH'

    def __init__(self):
        super(TestHandler, self).__init__()
