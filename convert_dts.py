import struct
import sys
from _lib3ds import ffi, lib


ChunkTypes = {}

class TSBasePart(object):
  def __init__(self):
    self.transform = 0
    self.IDnumber = 0
    self.radius = 0
    self.center = [0,0,0]

  @staticmethod
  def get_type():
    return 0x140005

  def load(self, dat, offset):
    (self.transform, self.IDnumber, self.radius, self.center[0], self.center[1], self.center[2]) = struct.unpack_from("<hHHhhh", dat, offset)
    offset = offset + 12
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSBasePart{\n")
    f.write("class: TSBasePart,\n")
    f.write(" transform: %d,\n"%(self.transform,))
    f.write(" IDnumber: %d,\n" % (self.IDnumber,))
    f.write(" radius: %d,\n" % (self.radius,))
    f.write(" center: {%d, %d, %d},\n" % (self.center[0],self.center[1],self.center[2]))
    if new:
      f.write("},\n")

class TSPartList(TSBasePart):
  def __init__(self):
    super(TSPartList,self).__init__()
    self.parts = []

  @staticmethod
  def get_type():
    return 0x140007

  @staticmethod
  def load_static(dat, offset):
    (t,l) = struct.unpack_from("<LL", dat, offset)
    offset = offset + 8
    rv = None
    if t in ChunkTypes:
      rv = ChunkTypes[t]()
#      print "loading %s statically" %(repr(rv))
      offset = rv.load(dat, offset)
#      print "finished loading %s" % (repr(rv))
    else:
      sys.stderr.write("couldn't find type %x"%(t,))
      offset = offset + l
      sys.exit(0)
    return (offset, rv)
    
  def load(self, dat, offset):
    offset = super(TSPartList,self).load(dat, offset)
    (count,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(count):
      new_part = 0
      (offset, new_part) = TSPartList.load_static(dat, offset)
      self.parts.append(new_part)
    return offset

  def debugOut(self, f, new=False):
    if new:
      f.write("TSPartList{\n")
    super(TSPartList,self).debugOut(f)
    f.write("class: TSPartList,\n")
    f.write("parts[%d]: {\n" %(len(self.parts),))
    for i in self.parts:
      i.debugOut(f, True)
    f.write(" },\n")
    if new:
      f.write("},\n")

class TSCellAnimPart(TSPartList):
  def __init__(self):
    super(TSCellAnimPart,self).__init__()
    self.animSequence = 0
  @staticmethod
  def get_type():
    return 0x14000b

  def load(self, dat, offset):
    offset = super(TSCellAnimPart,self).load(dat, offset)
    (self.animSequence,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSCellAnimPart{\n")
    super(TSCellAnimPart,self).debugOut(f)
    f.write("class: TSCellAnimPart,\n")
    f.write(" animSequence: %d,\n"% (self.animSequence,))
    if new:
      f.write("},\n")
  def modelOut(self, f, animList):
    for p in self.parts:
      p.modelOut(f, animList)

class TSGroup(TSBasePart):
  def __init__(self):
    super(TSGroup,self).__init__()
    self.indexes = []
    self.points = []
    self.colors = []
    self.items = []

  @staticmethod
  def get_type():
    return 0x140014

  def load(self, dat, offset):
    offset = super(TSGroup,self).load(dat, offset)
    (indexcount,pointcount,colorcount,itemcount) = struct.unpack_from("<HHHH", dat, offset)
    offset = offset + 8
    for i in range(indexcount):
      (new_index,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.indexes.append(new_index)
    for i in range(pointcount):
      (x,y,z) = struct.unpack_from("<hhh", dat, offset)
      offset = offset + 6
      self.points.append((x,y,z))
    for i in range(colorcount):
      (new_color,) = struct.unpack_from("<L", dat, offset)
      offset = offset + 4
      self.colors.append(new_color)
    for i in range(itemcount):
      (offset, new_item)= TSPartList.load_static(dat, offset)
      self.items.append(new_item)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSGroup{\n")
    super(TSGroup,self).debugOut(f)
    f.write("class: TSGroup,\n")
    f.write(" indexes[%d]: {\n" % (len(self.indexes)))
    for i in self.indexes:
      f.write("  %d,\n" %(i,))
    f.write(" },\n")
    f.write(" points[%d]: {\n" % (len(self.points)))
    for i in self.points:
      f.write("  {%ff, %ff, %ff},\n" %(i[0], i[1], i[2]))
    f.write(" },\n")
    f.write(" colors[%d]: {\n" % (len(self.colors)))
    for i in self.colors:
      f.write("  0x%x,\n" %(i,))
    f.write(" },\n")
    f.write(" items[%d]: {\n" % (len(self.items)))
    for i in self.items:
      i.debugOut(f, True)
    f.write(" },\n")
    if new:
      f.write("},\n")
  def modelOut(self, f, animList):
    m = lib.lib3ds_mesh_new("MeshId_%d_Transform_%d"%(self.IDnumber, self.transform))
    lib.lib3ds_mesh_new_point_list(m, len(self.points))
    

    r = {}
    for (p,c) in animList.relations:
      r[c] = p
    temp_t = ffi.new("Lib3dsMatrix")
    lib.lib3ds_matrix_identity(temp_t)
    tid = self.transform
    while tid != -1:
# ignore rotation transformations, below is untested/probably wrong
#      lib.lib3ds_matrix_translate_xyz(temp_t, -pivot[0], -pivot[1], -pivot[2])
#      lib.lib3ds_matrix_rotate_x(temp_t, -2.0*math.pi*animList.transforms[animList.defaultTransforms[tid]].r[0]/65535)
#      lib.lib3ds_matrix_rotate_y(temp_t, -2.0*math.pi*animList.transforms[animList.defaultTransforms[tid]].r[1]/65535)
#      lib.lib3ds_matrix_rotate_z(temp_t, -2.0*math.pi*animList.transforms[animList.defaultTransforms[tid]].r[2]/65535)
#      lib.lib3ds_matrix_translate_xyz(temp_t, pivot[0], pivot[1], pivot[2])
      lib.lib3ds_matrix_translate_xyz(temp_t,
        animList.transforms[animList.defaultTransforms[tid]].t[0],
        animList.transforms[animList.defaultTransforms[tid]].t[1],
        animList.transforms[animList.defaultTransforms[tid]].t[2])
      tid = r[tid]
# ignore rotation transformations, below is untested/probably wrong
#    lib.lib3ds_matrix_rotate_x(temp_t, 2*math.pi*animList.transforms[animList.defaultTransforms[self.transform]].r[0]/65535)
#    lib.lib3ds_matrix_rotate_y(temp_t, 2*math.pi*animList.transforms[animList.defaultTransforms[self.transform]].r[1]/65535)
#    lib.lib3ds_matrix_rotate_z(temp_t, 2*math.pi*animList.transforms[animList.defaultTransforms[self.transform]].r[2]/65535)
   
# it'd be nice if the tranformation matrix would apply via m.matrix, but
# haven't got that to have an effect... let's just apply to each point
# manually?
    temp_p_result = ffi.new("Lib3dsVector")
    temp_p_input = ffi.new("Lib3dsVector")
    for i in range(len(self.points)):
      temp_p_input[0] = self.points[i][0]
      temp_p_input[1] = self.points[i][1]
      temp_p_input[2] = self.points[i][2]
      lib.lib3ds_vector_transform(temp_p_result, temp_t, temp_p_input)
      m.pointL[i].pos[0] = temp_p_result[0]
      m.pointL[i].pos[1] = temp_p_result[1]
      m.pointL[i].pos[2] = temp_p_result[2]
    faces = []
    for item in self.items:
      if item.vertexCount < 3:
        continue
      for i in range(item.vertexCount-2):
        new_face = (item.normal, self.indexes[item.vertexList], self.indexes[item.vertexList+1+i], self.indexes[item.vertexList+2+i])
        faces.append(new_face)
    if len(faces) == 0:
      lib.lib3ds_mesh_free(m)
      return
    lib.lib3ds_mesh_new_face_list(m, len(faces))
    for i in range(len(faces)):
      m.faceL[i].points[0] = faces[i][1]
      m.faceL[i].points[1] = faces[i][2]
      m.faceL[i].points[2] = faces[i][3]
      m.faceL[i].normal[0] = self.points[faces[i][0]][0]
      m.faceL[i].normal[1] = self.points[faces[i][0]][1]
      m.faceL[i].normal[2] = self.points[faces[i][0]][2]
    lib.lib3ds_file_insert_mesh(f, m)
        

class TSPoly(object):
  def __init__(self):
    self.normal = 0
    self.center = 0
    self.vertexCount = 0
    self.vertexList = 0

  @staticmethod
  def get_type():
    return 0x140001

  def load(self, dat, offset):
    (self.normal, self.center, self.vertexCount, self.vertexList) = struct.unpack_from("<HHHH", dat, offset)
    offset = offset + 8
    return offset

  def debugOut(self, f, new=False):
    if new:
      f.write("TSPoly{\n")
    f.write("class: TSPoly,\nnormal: %d,\ncenter: %d,\nvertexCount: %d,\nvertexList: %d,\n" % (self.normal, self.center, self.vertexCount, self.vertexList))
    if new:
      f.write("},\n")
    
class TSSolidPoly(TSPoly):
  def __init__(self):
    super(TSSolidPoly,self).__init__()
    self.color = 0

  @staticmethod
  def get_type():
    return 0x140002

  def load(self, dat, offset):
    offset = super(TSSolidPoly,self).load(dat, offset)
    (self.color,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSSolidPoly{\n")
    super(TSSolidPoly,self).debugOut(f)
    f.write("class: TSSolidPoly,\n")
    f.write(" color: %d,\n" %(self.color,))
    if new:
      f.write("},\n")
    

class TSShadedPoly(TSSolidPoly):
  def __init__(self):
    super(TSShadedPoly,self).__init__()

  @staticmethod
  def get_type():
    return 0x140003

  def load(self, dat, offset):
    offset = super(TSShadedPoly,self).load(dat, offset)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSShadedPoly{\n")
    super(TSShadedPoly,self).debugOut(f)
    f.write("class: TSShadedPoly,\n")
    if new:
      f.write("},\n")

class TSTexture4Poly(TSSolidPoly):
  def __init__(self):
    super(TSTexture4Poly,self).__init__()

  @staticmethod
  def get_type():
    return 0x14000f

  def load(self, dat, offset):
    offset = super(TSTexture4Poly,self).load(dat, offset)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSTexture4Poly{\n")
    super(TSTexture4Poly,self).debugOut(f)
    f.write("class: TSTexture4Poly,\n")
    if new:
      f.write("},\n")


class TSBSPPart_node:
  def __init__(self):
    self.normal = [0,0,0]
    self.coeff = 0
    self.front = 0
    self.back = 0

  def load(self, dat, offset):
    (self.normal[0], self.normal[1], self.normal[2], self.coeff, self.front, self.back) = struct.unpack_from("<hhhlhh", dat, offset)
    offset = offset + 14
    return offset

  def debugOut(self, f):
    f.write(" { normal: {%d, %d, %d}, coeff: %d, front: %d, back: %d },\n" % (self.normal[0], self.normal[1], self.normal[2], self.coeff, self.front, self.back))

class TSBSPPart(TSPartList):
  def __init__(self):
    super(TSBSPPart,self).__init__()
    self.nodes = []
    self.transforms = []

  @staticmethod
  def get_type():
    return 0x140015

  def load(self, dat, offset):
    offset = super(TSBSPPart,self).load(dat, offset)
    (node_count,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(node_count):
      new_node = TSBSPPart_node()
      offset = new_node.load(dat, offset)
      self.nodes.append(new_node)

    for i in range(node_count):
      (new_transform,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.transforms.append(new_transform)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSBSPPart{\n")
    super(TSBSPPart,self).debugOut(f)
    f.write("class: TSBSPPart,\n")
    f.write(" nodes[%d]: {\n" % (len(self.nodes)))
    for n in self.nodes:
      n.debugOut(f)
    f.write(" },\n")
    f.write(" transforms[%d]: {\n" % (len(self.transforms)))
    for n in self.transforms:
      f.write("  %d,\n" % (n,))
    f.write(" },\n")
    if new:
      f.write("},\n")
  def modelOut(self, f, animList):
    for p in self.parts:
      p.modelOut(f, animList)

class TSShape(TSPartList):
  def __init__(self):
    super(TSShape,self).__init__()
    self.seqList1 = []
    self.seqList2 = []
    self.transformList = []

  @staticmethod
  def get_type():
    return 0x140008
  
  def load(self, dat, offset):
    offset = super(TSShape,self).load(dat, offset)
    (t,s) = struct.unpack_from("<HH", dat, offset)
    offset = offset + 4
    self.seqList2 = [0]*s
    for i in range(s):
      (a,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.seqList1.append(a)
    for i in range(t*16):
      (a,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.seqList1.append(a)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("TSShape{\n")
    super(TSShape,self).debugOut(f)
    f.write("class: TSShape,\n")
    f.write(" seqList1[%d]: {\n" % (len(self.seqList1)))
    for i in self.seqList1:
      f.write("  %d,\n" % (i,))
    f.write(" },\n")
    f.write(" seqList2[%d]: {\n" % (len(self.seqList2)))
    for i in self.seqList2:
      f.write("  %d,\n" % (i,))
    f.write(" },\n")
    f.write(" transformList[%d]: {\n" % (len(self.transformList)))
    for i in self.transformList:
      f.write("  %d,\n"% (i,))
    f.write(" },\n")
    if new:
      f.write("},\n")
    
    

class ANSequence_frame:
  def __init__(self):
    self.tick = 0
    self.numTransitions = 0
    self.firstTransition = 0
  def load(self, dat, offset):
    (self.tick, self.numTransitions, self.firstTransition) = struct.unpack_from("<HHH", dat, offset)
    offset = offset + 6
    return offset
  def debugOut(self, f):
    f.write("{ tick %d, numTransitions: %d, firstTransition: %d },\n" % (self.tick, self.numTransitions, self.firstTransition))

class ANSequence(object):
  def __init__(self):
    self.tick = 0
    self.priority = 0
    self.GM = 0
    self.frames = []
    self.parts = []
    self.transformIndices = []
  @staticmethod
  def get_type():
    return 0x1e0001

  def load(self, dat, offset):
    (self.tick, self.priority, self.GM) = struct.unpack_from("<HHH", dat, offset)
    offset = offset + 6
    (frameCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(frameCount):
      new_frame = ANSequence_frame()
      offset = new_frame.load(dat, offset)
      self.frames.append(new_frame)
    (partCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(partCount):
      (new_part,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.parts.append(new_part)
    for i in range(partCount*frameCount):
      (new_tindex,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.transformIndices.append(new_tindex)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("ANSequence{\n")
    f.write("class: ANSequence,\n")
    f.write(" tick: %d, priority: %d, GM: %d, \n" % (self.tick, self.priority, self.GM))
    f.write(" frames[%d]: {" % (len(self.frames)))
    for i in self.frames:
      i.debugOut(f)
    f.write(" },")
    f.write(" parts[%d]: {" % (len(self.parts)))
    for i in self.parts:
      f.write("  %d," %(i,))
    f.write(" },")
    f.write(" transformIndices[%d]: {" % (len(self.transformIndices)))
    for i in self.transformIndices:
      f.write("  %d," %(i,))
    f.write(" },")
    if new:
      f.write("},\n")
    
class ANCyclicSequence(ANSequence):
  def __init__(self):
    super(ANCyclicSequence,self).__init__()

  @staticmethod
  def get_type():
    return 0x1e0004

  def load(self, dat, offset):
    offset = super(ANCyclicSequence,self).load(dat, offset)
    return offset
  def debugOut(self, f, new=False):
    if new:
      f.write("ANCyclicSequence{\n")
    super(ANCyclicSequence,self).debugOut(f)
    f.write("class: ANCyclicSequence,\n")
    if new:
      f.write("},\n")


class ANAnimList_transition:
  def __init__(self):
    self.tick = 0
    self.destSequence = 0
    self.destFrame = 0
    self.groundMovement = 0

  def load(self, dat, offset):
    (self.tick, self.destSequence, self.destFrame, self.groundMovement) = struct.unpack_from("<HHHH", dat, offset)
    offset = offset + 8
    return offset
  def debugOut(self, f):
    f.write("{ tick: %d, destSequence: %d, destFrame: %d, groundMovement: %d }," %(self.tick, self.destSequence, self.destFrame, self.groundMovement))

class ANAnimList_transform:
  def __init__(self):
    self.r = [0,0,0]
    self.t = [0,0,0]

  def load(self, dat, offset):
    (self.r[0], self.r[1],self.r[2]) = struct.unpack_from("<HHH", dat, offset)
    offset = offset + 6
    (self.t[0], self.t[1],self.t[2]) = struct.unpack_from("<hhh", dat, offset)
    offset = offset + 6
    return offset
  def debugOut(self, f):
    f.write("{ r: {%d, %d, %d}, t: {%d, %d, %d}, }," %(self.r[0], self.r[1],self.r[2], self.t[0], self.t[1],self.t[2]))

class ANAnimList(object):
  def __init__(self):
    self.sequences = []
    self.transitions = []
    self.transforms = []
    self.defaultTransforms = []
    self.relations = []

  @staticmethod
  def get_type():
    return 0x1e0002

  def load(self, dat, offset):
    (sequenceCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(sequenceCount):
      (offset, new_item) = TSPartList.load_static(dat, offset)
      self.sequences.append(new_item)
    (transitionCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(transitionCount):
      new_transition = ANAnimList_transition()
      offset = new_transition.load(dat, offset)
      self.transitions.append(new_transition)
    (transformCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(transformCount):
      new_transform = ANAnimList_transform()
      offset = new_transform.load(dat, offset)
      self.transforms.append(new_transform)
    (defaultTransformCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(defaultTransformCount):
      (new_dtc,) = struct.unpack_from("<H", dat, offset)
      offset = offset + 2
      self.defaultTransforms.append(new_dtc)
    (relationsCount,) = struct.unpack_from("<H", dat, offset)
    offset = offset + 2
    for i in range(relationsCount):
      (a,b) = struct.unpack_from("<hh", dat, offset)
      offset = offset + 4
      self.relations.append((a,b))
    return offset

  def debugOut(self, f, new=False):
    if new:
      f.write("ANAnimList{\n")
    f.write("class: ANAnimList,")
    f.write(" sequences[%d]: {" % (len(self.sequences),))
    for i in self.sequences:
      i.debugOut(f,True)
    f.write(" },")
    f.write(" transitions[%d]: {" % (len(self.transitions),))
    for i in self.transitions:
      i.debugOut(f)
    f.write(" },")
    f.write(" transforms[%d]: {" % (len(self.transforms),))
    for i in self.transforms:
      i.debugOut(f)
    f.write(" },")
    f.write(" defaultTransforms[%d]: {" % (len(self.defaultTransforms),))
    for i in self.defaultTransforms:
      f.write(" %d," % (i,))
    f.write(" },")
    f.write(" relations[%d]: {" % (len(self.relations),))
    for i in self.relations:
      f.write(" { %d, %d }," % (i[0], i[1]))
    f.write(" },")
    if new:
      f.write("},\n")
      
    

class ANShape(TSShape):
  def __init__(self):
    super(ANShape,self).__init__()
    self.part = None

  @staticmethod
  def get_type():
    return 0x1e0003

  def load(self, dat, offset):
    offset = super(ANShape,self).load(dat, offset)
    (offset, self.part) = TSPartList.load_static(dat, offset)
    return offset

  def debugOut(self, f, new=False):
    if new:
      f.write("ANShape{\n")
    super(ANShape,self).debugOut(f)
    f.write("class: ANShape,\n")
    self.part.debugOut(f,True)
    if new:
      f.write("},\n")

  def modelOut(self, f):
    for p in self.parts:
      p.modelOut(f, self.part)

for k in (TSBasePart, TSPartList, TSShape, ANShape, TSBSPPart, TSGroup, TSPoly, TSShadedPoly, TSSolidPoly, TSTexture4Poly, TSCellAnimPart, ANAnimList, ANCyclicSequence, ANSequence):
  ChunkTypes[k.get_type()] = k
    

i = 0


if len(sys.argv) == 1:
  print "convert_dts.py [dtsfile1] [dtsfile2] ..."
  sys.exit(0)

for input_file in sys.argv[1:]:
  print "processing %s" %(input_file,)
  input_fd = open(input_file, "rb")

  dat = input_fd.read()

  input_fd.close()

  offset = 0
  if dat[0] != '\x02':
    print 'incorrect first byte!\n'
    continue

  offset = offset + 1

  (length, unk) = struct.unpack_from("<II", dat, offset)

  offset = offset + 8

  i = 0
  while offset < len(dat):
    (offset, val) = TSPartList.load_static(dat, offset)
    if type(val).__name__ == 'ANShape':
      f = lib.lib3ds_file_new() 
      val.modelOut(f)
      lib.lib3ds_file_save(f, "%s_ANShape%d.3ds" % (input_file,i,))
      i = i + 1
      lib.lib3ds_file_free(f)
