# MIT License

# Copyright (c) 2018-2019 Nathan Letwory, Joel Putnam, Tom Svilans

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import bpy
import rhino3dm as r3d
from mathutils import Matrix
from . import utils


#TODO
#tag collections and references with guids
#test w/ more complex blocks and empty blocks
#proper exception handling

    
def handle_instance_definitions(context, model, toplayer, layername, scale):
    """
    import instance definitions from rhino model as collections and recreate hierarchy of instances
    using collections and collection instances
    """
  
    if not layername in context.blend_data.collections:
            instance_col = context.blend_data.collections.new(name=layername)
            toplayer.children.link(instance_col)

    for idef in model.InstanceDefinitions:

        #TODO: tag collection with idef guid
        if not idef.Name in context.blend_data.collections:
            idef_col = context.blend_data.collections.new(name=idef.Name)
        else:
            idef_col = context.blend_data.collections[idef.Name]
            utils.tag_data(idef_col, idef.Id, idef.Name)

        try:
            instance_col.children.link(idef_col)
        except Exception:
            pass

def import_instance_reference(ob, context, n, layer, rhinomat, scale):
    #add an empty and set it up as a collection instance pointing to the collection given in "n"
    iref = bpy.data.objects.new('empty', None)
    iref.empty_display_size=1
    iref.empty_display_type='PLAIN_AXES'
    iref.instance_type='COLLECTION'
    iref.name=n
    iref.instance_collection = context.blend_data.collections[n]
    xform=list(ob.Geometry.Xform.ToFloatArray(1))
    xform=[xform[0:4],xform[4:8], xform[8:12], xform[12:16]]
    xform[0][3]*=scale 
    xform[1][3]*=scale 
    xform[2][3]*=scale 
    iref.matrix_world = Matrix(xform)
    utils.tag_data(iref, ob.Attributes.Id, ob.Attributes.Name)
                            
    #try to link iref into parent layer
    try:
        layer.objects.link(iref)
    except Exception:
        pass

def populate_instance_definitions(context, model, toplayer, layername):
    #for every instance definition fish out the instance definition objects and link them to their parent collection
    #this has to be done AFTER all
    for idef in model.InstanceDefinitions:
        #TODO: change this method! in a very large file this would loop through all objects for every single instance definition, possibly taking forever
        for ob in model.Objects:
            if ob.Attributes.Id in idef.GetObjectIds():
                children=[o for o in context.blend_data.objects if o.get('rhid', None) == str(ob.Attributes.Id)]
                print(children)
                #hen or egg guid'ed objects or instances!?
                for c in children:
                    try:
                        context.blend_data.collections[idef.Name].objects.link(c)
                    except Exception:
                        pass




