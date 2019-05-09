# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from decimal import Decimal


class MongoDBTypesTranslater():
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

  def translate(self, cdata):
    new_cdata = dict()

    for k, v in cdata.items():
      if type(v) == dict:
        new_cdata[k] = self.recode(v)
      else:
        new_cdata[k] = self._type_changer(v)
    
    return new_cdata
