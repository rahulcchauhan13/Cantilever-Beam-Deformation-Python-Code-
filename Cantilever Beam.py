# Cantilever Beam bending under the action of a uniform pressure
from abaqus import *
from abaqusConstants import *
import regionToolset

session.viewports['Viewport: 1'].setValues(displayedObject=None)

# Create the model
mdb.models.changeKey(fromName='Cantilever Beam', toName='Cantilever Beam')
beamModel= mdb.models['Cantilever Beam']

# Create the part
import sketch
import part
# sketch the beam cross-section using rectangle tool
beamProfileSketch = beamModel.ConstrainedSketch(name='Beam CS Profile',sheetSize=5)
beamProfileSketch.rectangle(point1=(0.1,0.1), point2=(0.3,-0.1))
# create 3D deformable part named Beam by extruding the sketch
beamPart = beamModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
beamPart.BaseSolidExtrude(sketch=beamProfileSketch, depth=5)

# create material
import material
beamMaterial = beamModel.Material(name='AISI 1005 Steel')
beamMaterial.Density(table=((7872, ), ))
beamMaterial.Elastic(table=((200E9, 0.29), ))

# Create solid section and assign the beam to it
import section
beamSection = beamModel.HomogeneousSolidSection(name='Beam Section', material = 'AISI 1005 Steel')

# Assign the beam to this Section
beam_region = (beamPart.cells,)
beamPart.SectionAssignment(region=beam_region, sectionName='Beam Section')

# Create the assembly
import assembly
beamAssembly = beamModel.rootAssembly
beamInstance = beamAssembly.Instance(name='Beam Instance', part=beamPart, dependent=ON)

# Create the step
import step
beamModel.StaticStep(name='Apply Load', previous='Initial', description='Load is applied during this step')

# Field output
beamModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Selected Field Outputs')
beamModel.fieldOutputRequests['Selected Field Outputs'].setValues(variables=('S','E','PEMAG','U','RF','CF'))

# history Output
beamModel.HistoryOutputRequest(name='Default History Outputs', createStepName='Apply Load', variables = PRESELECT)
del beamModel.historyOutputRequests['H-Output-1']

# apply Load
top_face_pt_x = 0.2
top_face_pt_y = 0.1
top_face_pt_z = 2.5
top_face_pt = (top_face_pt_x, top_face_pt_y, top_face_pt_z)
top_face = beamInstance.faces.findAt((top_face_pt,))
top_face_region = regionToolset.Region(side1Faces=top_face)
beamModel.Pressure(name='Uniform Applied Pressure',createStepName = 'Apply Load', region = top_face_region, distributionType = UNIFORM, magnitude = 10, amplitude = UNSET)

# Boundary condition
fixed_end_face_pt_x = 0.2
fixed_end_face_pt_y = 0
fixed_end_face_pt_z = 0
fixed_end_face_pt = (fixed_end_face_pt_x, fixed_end_face_pt_y, fixed_end_face_pt_z)
fixed_end_face = beamInstance.faces.findAt((fixed_end_face_pt,))
fixed_end_face_region = regionToolset.Region(faces=fixed_end_face)
beamModel.EncastreBC(name='Encastre one end', createStepName = 'Initial', region = fixed_end_face_region)

# Mesh
import mesh
beam_inside_xcoord = 0.2
beam_inside_ycoord = 0
beam_inside_zcoord = 2.5
elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary = STANDARD, kinematicSplit = AVERAGE_STRAIN, secondOrderAccuracy = OFF, hourglassControl = DEFAULT, distortionControl = DEFAULT)
beamCells = beamPart.cells
selectedBeamCells = beamCells.findAt((beam_inside_xcoord,beam_inside_ycoord,beam_inside_zcoord),)
beamMeshRegion = (selectedBeamCells,)
beamPart.setElementType(regions=beamMeshRegion, elemTypes=(elemType1,))
beamPart.seedPart(size=0.06, deviationFactor=0.1)
beamPart.generateMesh()

# create job
import job
mdb.Job(name='Cantilever_Beam_Job', model='Cantilever Beam', type = ANALYSIS, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, description = 'Job simulates a loaded cantilever beam', parallelizationMethodExplicit=DOMAIN, multiprocessingMode = DEFAULT, numDomains = 1, userSubroutine='',numCpus = 1, memory=50, memoryUnits=PERCENTAGE, scratch='', echoPrint=OFF, modelPrint=OFF,contactPrint=OFF, historyPrint=OFF)
mdb.jobs['Cantilever_Beam_Job'].submit(consistencyChecking=OFF)
mdb.jobs['Cantilever_Beam_Job'].waitForCompletion()

# Visualization
import visualization
beam_viewport = session.Viewport(name = 'Beam Results Viewport')
beam_Odb_Path = 'Cantilever_Beam_Job.odb'
an_odb_objet = session.openOdb(name = beam_Odb_Path)
beam_viewport.setValues(displayedObject=an_odb_objet)
beam_viewport.odbDisplay.display.setValues(plotState=(DEFORMED,))
