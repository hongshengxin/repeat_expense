# _*_ coding: UTF-8 _*_
'''
企业定制的实体类型，和实体的字符枚举值，用于ner时定制企业的命名实体

系统级的实体类型不通过此种方式

'''
from typing import Text, List, Dict, Set
import copy


def _is_valid_entity(entity: Dict):
    value = entity.get("entity_value")
    if value is None:
        return False
    value = value.strip()
    if len(value) == 0:
        return False
    entity_type = entity.get("entity_type")
    if entity_type is None:
        return False
    entity_type = entity_type.strip()
    if len(entity_type) == 0:
        return False
    return True


class OrgEntityType(object):

    def __init__(self, org_id: Text, entity_values: List[Dict]):
        self.org_id = org_id
        self.entity_type_dict = {}  # entity_type -> set(word)
        self.entity_dict = {}  # word->set(entity_type)

        for entity in entity_values:
            if not _is_valid_entity(entity):
                continue

            entity_value = entity.get("entity_value")
            entity_type = entity.get("entity_type")

            if entity_value not in self.entity_dict:
                self.entity_dict[entity_value] = set()
            self.entity_dict[entity_value].add(entity_type)

            if entity_type not in self.entity_type_dict:
                self.entity_type_dict[entity_type] = set()
            self.entity_type_dict[entity_type].add(entity_value)

    def add_entity(self, entity_type: Text, entity_value: Text):
        if not _is_valid_entity({"entity_type": entity_type, "entity_value": entity_value}):
            raise ValueError("无效的entity_type:{}, entity_value:{}".format(entity_type, entity_value))

        if entity_value not in self.entity_dict:
            self.entity_dict[entity_value] = set()
        self.entity_dict[entity_value].add(entity_type)

        if entity_type not in self.entity_type_dict:
            self.entity_type_dict[entity_type] = set()
        self.entity_type_dict[entity_type].add(entity_value)

    def remove_entity(self, entity_type: Text, entity_value: Text):
        if not _is_valid_entity({"entity_type": entity_type, "entity_value": entity_value}):
            raise ValueError("无效的entity_type:{}, entity_value:{}".format(entity_type, entity_value))

        if entity_value not in self.entity_dict:
            return
        self.entity_dict[entity_value].remove(entity_type)
        if len(self.entity_dict[entity_value]) == 0:
            self.entity_dict.pop(entity_value)

        self.entity_type_dict[entity_type].remove(entity_value)
        if len(self.entity_type_dict[entity_type]) == 0:
            self.entity_type_dict.pop(entity_type)

    def get_entity_dict(self):
        '''
        提供给DictTagger，添加用户定义实体类型
        :return:
        '''
        return self.entity_dict

    def get_all_entity_types(self):
        return self.entity_type_dict.keys()

    def get_entity_type_values(self, entity_type):
        return copy.copy(self.entity_type_dict.get(entity_type))

    @classmethod
    def create_from_entities(cls, org_id: Text, entities: Dict[Text, Set[Text]]):
        instance = OrgEntityType(org_id, [])
        for word, entity_set in entities.items():
            for entity_type in entity_set:
                instance.add_entity(entity_type, word)
        return instance
