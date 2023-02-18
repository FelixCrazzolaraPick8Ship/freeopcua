"""
Generate address space c++ code from xml file specification
"""
import sys

import xml.etree.ElementTree as ET

class ObjectStruct(object):
    def __init__(self):
        self.nodetype = None
        self.nodeid = None
        self.browsename = None 
        self.displayname = None
        self.symname = None
        self.parent = None
        self.parentlink = None
        self.desc = ""
        self.typedef = None
        self.refs = []
        self.nodeclass = None
        self.eventnotifier = 0 

        #variable
        self.datatype = None
        self.rank = -1 # check default value
        self.value = []
        self.dimensions = None
        self.accesslevel = None 
        self.useraccesslevel = None
        self.minsample = None

        #referencetype
        self.inversename = ""
        self.abstract = "false"
        self.symmetric = "false"

        #datatype
        self.definition = []

        #types


class RefStruct():
    def __init__(self):
        self.reftype = None
        self.forward = "true"
        self.target = None


class CodeGenerator(object):
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.output_file = None
        self.part = self.input_path.split(".")[-2]

    def run(self):
        sys.stderr.write("Generating C++ {} for XML file {}".format(self.output_path, self.input_path) + "\n")
        if sys.version_info < (3,):
          import codecs
          self.output_file = codecs.open(self.output_path, 'w', 'utf-8')
        else:
          self.output_file = open(self.output_path, "w")
        self.make_header()
        tree = ET.parse(xmlpath)
        root = tree.getroot()
        for child in root:
            if child.tag[51:] == 'UAObject':
                node = self.parse_node(child)
                self.make_object_code(node)
            elif child.tag[51:] == 'UAObjectType':
                node = self.parse_node(child)
                self.make_object_type_code(node)
            elif child.tag[51:] == 'UAVariable':
                node = self.parse_node(child)
                self.make_variable_code(node)
            elif child.tag[51:] == 'UAVariableType':
                node = self.parse_node(child)
                self.make_variable_type_code(node)
            elif child.tag[51:] == 'UAReferenceType':
                node = self.parse_node(child)
                self.make_reference_code(node)
            elif child.tag[51:] == 'UADataType':
                node = self.parse_node(child)
                self.make_datatype_code(node)
            elif child.tag[51:] == 'UAMethod':
                node = self.parse_node(child)
                self.make_method_code(node)
            else:
                sys.stderr.write("Not implemented node type: " + child.tag[51:] + "\n")
        self.writecode('''
void CreateAddressSpace%s(OpcUa::NodeManagementServices & registry)
{''' % (self.part))
        for child in root:
            if child.tag[51:] == 'UAObject':
                pass
            elif child.tag[51:] == 'UAObjectType':
                pass
            elif child.tag[51:] == 'UAVariable':
                pass
            elif child.tag[51:] == 'UAVariableType':
                pass
            elif child.tag[51:] == 'UAReferenceType':
                pass
            elif child.tag[51:] == 'UADataType':
                pass
            elif child.tag[51:] == 'UAMethod':
                pass
            else:
                continue
            node = self.parse_node(child)
            self.writecode(" ", 'create_{}(registry);'.format(node.nodeid[2:]))
        self.make_footer()

    def writecode(self, *args):
        self.output_file.write(" ".join(args) + "\n")

    def make_header(self, ):
        self.writecode('''
// DO NOT EDIT THIS FILE!
// It is automatically generated from opcfoundation.org schemas.
//

#include "standard_address_space_parts.h"
#include <opc/ua/protocol/string_utils.h>
#include <opc/common/addons_core/addon.h>
#include <opc/ua/protocol/strings.h>
#include <opc/ua/protocol/variable_access_level.h>
#include <opc/ua/services/node_management.h>

#include <algorithm>
#include <iostream>
#include <map>

namespace OpcUa
{''')

    def make_footer(self, ):
        self.writecode('''
}

} // namespace
''')


    def parse_node(self, child):
        obj = ObjectStruct()
        obj.nodetype = child.tag[53:]
        for key, val in child.attrib.items():
            if key == "NodeId":
                obj.nodeid = val
            elif key == "BrowseName":
                obj.browsename = val
            elif key == "SymbolicName":
                obj.symname = val
            elif key == "ParentNodeId":
                obj.parent = val
            elif key == "DataType":
                obj.datatype = val
            elif key == "IsAbstract":
                obj.abstract = val
            elif key == "EventNotifier":
                obj.eventnotifier = val
            elif key == "ValueRank":
                obj.rank = val
            elif key == "ArrayDimensions":
                obj.dimensions = val
            elif key == "MinimumSamplingInterval":
                obj.minsample = val
            elif key == "AccessLevel":
                obj.accesslevel = val
            elif key == "UserAccessLevel":
                obj.useraccesslevel = val
            elif key == "Symmetric":
                obj.symmetric = val
            else:
                sys.stderr.write("Attribute not implemented: " + key + " " + val + "\n")

        obj.displayname = obj.browsename#FIXME
        for el in child:
            tag = el.tag[51:]

            if tag == "DisplayName":
                obj.displayname = el.text
            elif tag == "Description":
                obj.desc = el.text
            elif tag == "References":
                for ref in el:
                    #self.writecode("ref", ref, "IsForward" in ref, ref.text )
                    if ref.attrib["ReferenceType"] == "HasTypeDefinition":
                        obj.typedef = ref.text
                    elif "IsForward" in ref.attrib and ref.attrib["IsForward"] == "false":
                        #if obj.parent:
                            #sys.stderr.write("Parent is already set with: "+ obj.parent + " " + ref.text + "\n") 
                        obj.parent = ref.text
                        obj.parentlink = ref.attrib["ReferenceType"]
                    else:
                        struct = RefStruct()
                        if "IsForward" in ref.attrib: struct.forward = ref.attrib["IsForward"]
                        struct.target = ref.text
                        struct.reftype = ref.attrib["ReferenceType"] 
                        obj.refs.append(struct)
            elif tag == "Value":
                for val in el:
                    ntag = val.tag[47:]
                    if ntag == "Int32":
                        obj.value.append("(int32_t) " + val.text)
                    elif ntag == "UInt32":
                        obj.value.append("(uint32_t) " + val.text)
                    elif ntag in ('ByteString', 'String'):
                        mytext = val.text.replace('\r', '')
                        if len(mytext) < 65535:
                            mytext = ['"{}"'.format(x) for x in val.text.replace('\r', '').splitlines()]
                            mytext = '\n'.join(mytext)
                            obj.value.append('+{}'.format(mytext))
                        else:
                            def batch_gen(data, batch_size):
                                for i in range(0, len(data), batch_size):
                                    yield data[i:i+batch_size]
                            mytext = '({}).c_str()'.format(
                                ' +\n'.join(
                                    ['std::string({})'.format(
                                        '\n'.join(
                                            ['"{}"'.format(x) for x in segment.splitlines()]
                                        )
                                     ) for segment in batch_gen(mytext, 65000)
                                    ]
                                )
                            )
                    elif ntag == "ListOfExtensionObject":
                        pass
                    elif ntag == "ListOfLocalizedText":
                        pass
                    else:
                        self.writecode("Missing type: ", ntag)
            elif tag == "InverseName":
                obj.inversename = el.text
            elif tag == "Definition":
                for field in el:
                    obj.definition.append(field)
            else:
                sys.stderr.write("Not implemented tag: "+ str(el) + "\n")
        return obj

    def make_node_code(self, obj, indent):
        self.writecode(indent, 'AddNodesItem node;')
        self.writecode(indent, 'node.RequestedNewNodeId = ToNodeId("{}");'.format(obj.nodeid))
        self.writecode(indent, 'node.BrowseName = ToQualifiedName("{}");'.format(obj.browsename))
        self.writecode(indent, 'node.Class = NodeClass::{};'.format(obj.nodetype))
        if obj.parent: self.writecode(indent, 'node.ParentNodeId = ToNodeId("{}");'.format(obj.parent))
        if obj.parent: self.writecode(indent, 'node.ReferenceTypeId = {};'.format(self.to_ref_type(obj.parentlink)))
        if obj.typedef: self.writecode(indent, 'node.TypeDefinition = ToNodeId("{}");'.format(obj.typedef))

    def to_vector(self, dims):
        s = "std::vector<uint32_t> {"
        s += dims.replace(',', ', ')
        s += "}"
        return s

    def to_data_type(self, nodeid):
        if not nodeid:
            return "ObjectId::String"
        if "=" in nodeid:
            return 'ToNodeId("{}")'.format(nodeid)
        else:
            return 'ObjectId::{}'.format(nodeid)

    def to_ref_type(self, nodeid):
        if "=" in nodeid:
            return 'ToNodeId("{}")'.format(nodeid)
        else:
            return 'ReferenceId::{}'.format(nodeid)

    def make_object_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'ObjectAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        self.writecode(indent, 'attrs.EventNotifier = {};'.format(obj.eventnotifier))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_object_type_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'ObjectTypeAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        self.writecode(indent, 'attrs.IsAbstract = {};'.format(obj.abstract))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")


    def make_variable_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'VariableAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        self.writecode(indent, 'attrs.Type = {};'.format(self.to_data_type(obj.datatype)))
        if obj.value and len(obj.value) == 1: self.writecode(indent, 'attrs.Value = {};'.format(obj.value[0]))
        if obj.rank: self.writecode(indent, 'attrs.Rank = {};'.format(obj.rank))
        if obj.accesslevel: self.writecode(indent, 'attrs.AccessLevel = (VariableAccessLevel) {};'.format(obj.accesslevel))
        if obj.useraccesslevel: self.writecode(indent, 'attrs.UserAccessLevel = (VariableAccessLevel) {};'.format(obj.useraccesslevel))
        if obj.minsample: self.writecode(indent, 'attrs.MinimumSamplingInterval = {};'.format(obj.minsample))
        if obj.dimensions: self.writecode(indent, 'attrs.Dimensions = {};'.format(self.to_vector(obj.dimensions)))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_variable_type_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'VariableTypeAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        self.writecode(indent, 'attrs.Type = {};'.format(self.to_data_type(obj.datatype)))
        if obj.value and len(obj.value) == 1: self.writecode(indent, 'attrs.Value = {};'.format(obj.value[0]))
        if obj.rank: self.writecode(indent, 'attrs.Rank = {};'.format(obj.rank))
        if obj.abstract: self.writecode(indent, 'attrs.IsAbstract = {};'.format(obj.abstract))
        if obj.dimensions: self.writecode(indent, 'attrs.Dimensions = {};'.format(self.to_vector(obj.dimensions)))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_method_code(self, obj):
        indent = "   "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'MethodAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_reference_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'ReferenceTypeAttributes attrs;')
        if obj.desc: self.writecode(indent, 'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        if obj. inversename: self.writecode(indent, 'attrs.InverseName = LocalizedText("{}");'.format(obj.inversename))
        if obj.abstract: self.writecode(indent, 'attrs.IsAbstract = {};'.format(obj.abstract))
        if obj.symmetric: self.writecode(indent, 'attrs.Symmetric = {};'.format(obj.symmetric))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_datatype_code(self, obj):
        indent = " "
        self.writecode("")
        self.writecode('static void create_{}(OpcUa::NodeManagementServices & registry)'.format(obj.nodeid[2:]))
        self.writecode("{")
        self.make_node_code(obj, indent)
        self.writecode(indent, 'DataTypeAttributes attrs;')
        if obj.desc: self.writecode(indent, u'attrs.Description = LocalizedText("{}");'.format(obj.desc))
        self.writecode(indent, 'attrs.DisplayName = LocalizedText("{}");'.format(obj.displayname))
        if obj.abstract: self.writecode(indent, 'attrs.IsAbstract = {};'.format(obj.abstract))
        self.writecode(indent, 'node.Attributes = attrs;')
        self.writecode(indent, 'registry.AddNodes(std::vector<AddNodesItem> {node});')
        self.make_refs_code(obj, indent)
        self.writecode("}")

    def make_refs_code(self, obj, indent):
        if not obj.refs:
            return
        self.writecode(indent, "std::vector<AddReferencesItem> refs;")
        for ref in obj.refs:
            self.writecode(indent, "{")
            localIndent = indent + "  "
            self.writecode(localIndent, 'AddReferencesItem ref;')
            self.writecode(localIndent, 'ref.IsForward = true;')
            self.writecode(localIndent, 'ref.ReferenceTypeId = {};'.format(self.to_ref_type(ref.reftype)))
            self.writecode(localIndent, 'ref.SourceNodeId = ToNodeId("{}");'.format(obj.nodeid))
            self.writecode(localIndent, 'ref.TargetNodeClass = NodeClass::DataType;')
            self.writecode(localIndent, 'ref.TargetNodeId = ToNodeId("{}");'.format(ref.target))
            self.writecode(localIndent, "refs.push_back(ref);")
            self.writecode(indent, "}")
        self.writecode(indent, 'registry.AddReferences(refs);')


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "all":
        for i in (3, 4, 5, 8, 9, 10, 11, 13):
            xmlpath = "Opc.Ua.NodeSet2.Part{}.xml".format(str(i))
            cpppath = "../src/server/standard_address_space_part{}.cpp".format(str(i))
            c = CodeGenerator(xmlpath, cpppath)
            c.run()


    elif len(sys.argv) != 3:
        print(sys.argv)
        print("usage: generate_address_space.py xml_input_file cpp_output_file")
        print(" or generate_address_space.py all")
        sys.exit(1)
    else:
        xmlpath = sys.argv[1] 
        cpppath = sys.argv[2]
    c = CodeGenerator(xmlpath, cpppath)
    c.run()

