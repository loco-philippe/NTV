# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 22:24:59 2022

@author: philippe@loco-labs.io

The `NTV.json_ntv.ntv_comment` module contains the `NtvComment` class.
"""

import json
from json_ntv.ntv_patch import NtvPatch


class NtvComment:
    """This class includes comments and change management methods for NTV entities :

    *Attributes :*

    - **_ntv** : Ntv entity being commented on
    - **_comments**:  list of NtvPatch to apply to the NTV entity

    *dynamic values (@property)*
    - `comments`
    - `ntv`

    *instance method*
    - `add`
    - `accept`
    - `reject`
    - `json`
    """

    def __init__(self, ntv, comments=None):
        """constructor

        *Parameters*

        - **ntv**: Ntv - NTV entity being commented on
        - **comments**: list of NtvPatch (default None) - comments applied to the entity
        """
        self._ntv = ntv
        self._comments = []
        if not comments:
            return
        if comments.__class__.__name__ in ("NtvPatch", "NtvOp"):
            self._comments = [NtvPatch(comments)]
        elif isinstance(comments, list):
            self._comments = [NtvPatch(comment) for comment in comments]

    def __repr__(self):
        """string representation"""
        if not self._comments:
            return "no comments"
        return json.dumps(self.json())

    def __eq__(self, other):
        """equal if _comments and _ntv are equal"""
        return (
            self.__class__.__name__ == other.__class__.__name__
            and self._ntv == other._ntv
            and self._comments == other._comments
        )

    @property
    def comments(self):
        """getters _comments"""
        return self._comments

    @property
    def ntv(self):
        """getters _ntv"""
        return self._ntv

    def add(self, comment=None):
        """add comment in the list of comments

        *Parameters*

        - **comment**: NtvPatch (default None) - new comment to apply
        """
        self._comments.append(NtvPatch(comment))
        return len(self._comments) - 1

    def reject(self, all_comment=False):
        """remove the last or all comments

        *Parameters*

        - **all_comment**: Boolean (default False) - if False, remove the last comment

        *return*: resulting NtvComment
        """
        if all_comment or len(self._comments) <= 1:
            return NtvComment(self._ntv, [])
        return NtvComment(self._ntv, self._comments[:-1])

    def accept(self, all_comment=True):
        """apply the first or all comments

        *Parameters*

        - **all_comment**: Boolean (default True) - if False, apply the first comment

        *return*: resulting NtvComment
        """
        if not self._comments:
            return NtvComment(self._ntv, self._comments)
        apply = self._comments if all_comment else [self._comments[0]]
        ntv = self._ntv
        for comment in apply:
            ntv = comment.exe(ntv)
        return NtvComment(ntv, [] if all_comment else self._comments[1:])

    def json(self, ntv=False, comments=True):
        """return json-value.

        *Parameters*

        - **ntv**: Boolean (default False) - if True, include ntv
        - **comments**: Boolean (default True) - if True, include comments

        *return*: resulting json-value
        """
        jsn = {}
        if self._comments and comments:
            jsn["comments"] = [comment.json for comment in self._comments]
        if ntv:
            jsn["ntv"] = self._ntv.to_obj()
        return jsn
