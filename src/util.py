#!/usr/bin/env python
# Copyright 2011 Penny Arcade, Inc. All Rights Reserved.

"Helper utilities for ShopifyAPI"

try:
    from functools import partial
except ImportError:
    # Python 2.4 compatability
    def partial(func, *args, **kwargs):
        def _partial(*moreargs, **morekwargs):
            return func(*(args + moreargs), **dict(kwargs, **morekwargs))
        return _partial

