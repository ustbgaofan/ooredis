# coding:utf-8

__all__ = ['Dict']

__metaclass__ = type

import redis
import collections

from base_key import BaseKey
from helper import format_key, wrap_exception
from common_key_property_mixin import CommonKeyPropertyMixin

DELETE_FAIL_CAUSE_KEY_NOT_EXISTS = False

class Dict(BaseKey, CommonKeyPropertyMixin, collections.MutableMapping):

    """
    将 Redis 的 Hash 结构映射为字典对象。
    """

    def __repr__(self):
        return format_key(self, self.name, dict(self))


    @wrap_exception
    def __contains__(self, key):
        """
        检查字典是否包含给定 key 。

        Args:
            key

        Time:
            O(1)

        Returns:
            bool

        Raises:
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        return self._client.hexists(self.name, key)
    

    @wrap_exception
    def __setitem__(self, key, python_value):
        """ 
        将字典中键 key 的值设为 python_value 。
        如果键 key 已经关联了另一个值 ，那么将它覆盖。

        Args:
            key
            python_value

        Time:
            O(1)

        Returns:
            None

        Raises:
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        redis_value = self._encode(python_value)
        self._client.hset(self.name, key, redis_value)


    @wrap_exception
    def __getitem__(self, key):
        """ 
        返回字典中键 key 的值。
        如果键 key 在字典中不存在，那么抛出 KeyError 。

        Args:
            key

        Time:
            O(1)

        Returns:
            python_value

        Raises:
            KeyError: key 不存在时抛出。
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        redis_value = self._client.hget(self.name, key)
        if redis_value is None:
            raise KeyError

        python_value = self._decode(redis_value)
        return python_value

    
    @wrap_exception
    def __delitem__(self, key):
        """ 
        删除字典键 key 的值。
        如果键 key 的值不存在，那么抛出 KeyError 。

        Args:
            key

        Time:
            O(1)

        Returns:
            None

        Raises:
            KeyError: key 不存在时抛出。
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        status = self._client.hdel(self.name, key)
        if status == DELETE_FAIL_CAUSE_KEY_NOT_EXISTS:
            raise KeyError


    # @wrap_exception
    # 似乎因为 yield 的缘故，装饰器没办法在这里使用
    def __iter__(self):
        """ 
        返回一个包含字典里所有键的迭代器。

        Args:
            None

        Time:
            O(N)

        Returns:
            iterator
        
        Raises:
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        try:
            for key in self._client.hkeys(self.name):
                yield key
        except redis.exceptions.ResponseError:
            raise TypeError

   
    @wrap_exception
    def __len__(self):
        """
        返回字典中键-值对的个数。
        空字典返回 0 。

        Args:
            None

        Time:
            O(1)

        Returns:
            len

        Raises:
            TypeError: Key 对象不是 Dict 类型时抛出。
        """
        return self._client.hlen(self.name)
