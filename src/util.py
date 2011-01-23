#!/usr/bin/env python
# Copyright 2011 Erik Karulf. All Rights Reserved.

"Helper utilities for ShopifyAPI"

try:
    from functools import partial
except ImportError:
    # Python 2.4 compatability
    def partial(func, *args, **kwargs):
        def _partial(*moreargs, **morekwargs):
            return func(*(args + moreargs), **dict(kwargs, **morekwargs))
        return _partial

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

