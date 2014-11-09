from JumpScale import j

MAIN="""
{

    "apiVersion": "1.0.0",
    "swaggerVersion": "1.2",
    "basePath": "http://petstore.swagger.wordnik.com/api",
    "resourcePath": "/pet",
    "produces": [
        "application/json",
        "application/xml",
        "text/plain",
        "text/html"
    ],
    {{apis}}
    {{models}}
}
"""

APIS="""
"""

MODELS="""
"""

POSTPARAMS="""
            [
                {
                    "name": "{{name}}Id",
                    "description": "ID of {{name}} that needs to be updated",
                    "required": true,
                    "type": "string",
                    "paramType": "path",
                    "allowMultiple": false
                },
                {
                    "name": "name",
                    "description": "Updated name of the {{name}}",
                    "required": false,
                    "type": "string",
                    "paramType": "form",
                    "allowMultiple": false
                },
                {
                    "name": "status",
                    "description": "Updated status of the {{name}}",
                    "required": false,
                    "type": "string",
                    "paramType": "form",
                    "allowMultiple": false
                }
            ]
"""

class MongoEngineGenerator():
    def __init__(self,dest):
        self.dest=dest
        j.system.fs.createDir(j.system.fs.getDirName(self.dest))

    def generate(self,spec):
        out="from mongoengine import *\n\n"
        out+="classes=[]\n"
        for modelname in spec.keys():
            spec2=spec[modelname]
            out="%s%s\n"%(out,self.generateModel(modelname,spec2))

        j.system.fs.writeFile(filename=self.dest,contents=out)        

    def generateModel(self,name,modelspec):
        classname="%s_%s"%(modelspec["actorname"],name)
        out="class %s(Document):\n"%classname
        
        for propspec in modelspec["properties"]:
            name=propspec["name"].lower().strip()
            descr=propspec["description"]
            if not(descr==None or descr==""):
                help_str="help_text='%s',"%descr
            else:
                help_str=""
            tags=propspec["tags"]
            if tags<>None and tags<>'':
                pass
                #need to insert code for references
                
            ttype=propspec["type"]
            default=propspec["default"]
            args=""
            if default==None:
                default_str=""
                required_str="required=True,"
            else:
                if ttype in ["str"]:
                    default_str="default=%s,"%default
                else:
                    default_str="default='%s',"%default
                required_str="required=False,"

            def type2typestr(ttype):
                if ttype=="str":
                    ttypestr="StringField"
                elif ttype=="int":
                    ttypestr="IntField"
                elif ttype=="bool":
                    ttypestr="BooleanField"
                else:
                    from IPython import embed
                    print "DEBUG NOW unknown in MongoEngineGenerator type2typestr"
                    embed()
                    p                    
                return ttypestr

            if ttype.find("list")==0:
                ttype=ttype.split("(",1)[1]
                ttype=ttype.split(")",1)[0]
                args+=help_str
                args=args.rstrip(",")
                out+="    %s =  ListField(%s(), default=list,%s)\n"%(name,type2typestr(ttype),args)

            elif ttype.find("dict")==0:
                ttype=ttype.split("(",1)[1]
                ttype=ttype.split(")",1)[0]
                args+=help_str
                args=args.rstrip(",")
                out+="    %s =  ListField(field=%s(), default=list,%s)\n"%(name,type2typestr(ttype),args)
                
            else:
                args+=required_str
                args+=default_str
                args+=help_str
                args=args.rstrip(",")
                out+="    %s = %s(%s)\n"%(name,type2typestr(ttype),args)


        out+="classes.append(%s)\n"%classname


        return out
        

    # BinaryField
    # BooleanField
    # ComplexDateTimeField
    # DateTimeField
    # DecimalField
    # DictField
    # DynamicField
    # EmailField
    # EmbeddedDocumentField
    # FileField
    # FloatField
    # GenericEmbeddedDocumentField
    # GenericReferenceField
    # GeoPointField
    # ImageField
    # IntField
    # ListField
    # MapField
    # ObjectIdField
    # ReferenceField
    # SequenceField
    # SortedListField
    # StringField
    # URLField
    # UUIDField
    # PointField
    # LineStringField
    # PolygonField
    # MultiPointField
    # MultiLineStringField
    # MultiPolygonField
