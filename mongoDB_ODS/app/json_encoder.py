# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Copyright 2019 Digital Asset (Switzerland) GmbH and/or its affiliates.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from decimal import Decimal


class JSONEncoder():
  def _type_changer(self, arg):
    if type(arg) == Decimal:
      return float(arg)
    elif type(arg) == list:
      nl = []
      for a in arg:
        n = self._type_changer(a)
        nl.append(n)
      return nl
    else:
      return arg

  def recode(self, cdata):
    new_cdata = dict()

    for k, v in cdata.items():
      if type(v) == dict:
        new_cdata[k] = self.recode(v)
      else:
        new_cdata[k] = self._type_changer(v)
    
    return new_cdata

