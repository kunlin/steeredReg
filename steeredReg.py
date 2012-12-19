#Modefied version based on Steve Pieper's Regmatic.py by Kunlin Cao (GE Research) on 06/22/2012

from __main__ import vtk, qt, ctk, slicer
from math import *

#
# steeredReg
#

class steeredReg:
  def __init__(self, parent):
    parent.title = "steeredReg"
    parent.categories = ["Registration"]
    parent.dependencies = []
    parent.contributors = ["Steve Pieper (Isomics), Kunlin Cao (GE)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Steerable registration example as a scripted loadable extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Steve Pieper and was partially funded by NIH grant 3P41RR013218.
    Kunlin Cao continued to develope the interaction part.
""" # replace with organization, grant and thanks.
    self.parent = parent

#
# qsteeredRegWidget
#

class steeredRegWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

    self.logic = steeredRegLogic()
    self.interaction = False
    
##    self.parameterNode = None
##    self.parameterNodeTag = None
##
##    # connections is a list of widget/signal/slot tripples
##    # for the options gui that can be connected/disconnected
##    # as needed to prevent triggering mrml updates while
##    # updating the state of the gui
##    # - each level of the inheritance tree can add entries
##    #   to this list for use by the connectWidgets
##    #   and disconnectWidgets methods
##    self.connections = []
##    self.connectionsConnected = False
##
##    # 1) find the parameter node in the scene and observe it
##    # 2) set the defaults (will only set them if they are not
##    # already set)
##    self.updateParameterNode(self.parameterNode, vtk.vtkCommand.ModifiedEvent)
##    self.setMRMLDefaults()
##
##    # TODO: change this to look for specfic events (added, removed...)
##    # but this requires being able to access events by number from wrapped code
##    tag = slicer.mrmlScene.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateParameterNode)
##    self.observerTags.append( (slicer.mrmlScene, tag) )

  def __del__(self):
    self.destroy()
    if self.parameterNode:
      self.parameterNode.RemoveObserver(self.parameterNodeTag)
    for tagpair in self.observerTags:
      tagpair[0].RemoveObserver(tagpair[1])

  def connectWidgets(self):
    if self.connectionsConnected: return
    for widget,signal,slot in self.connections:
      success = widget.connect(signal,slot)
      if not success:
        print("Could not connect {signal} to {slot} for {widget}".format(
          signal = signal, slot = slot, widget = widget))
    self.connectionsConnected = True

  def disconnectWidgets(self):
    if not self.connectionsConnected: return
    for widget,signal,slot in self.connections:
      success = widget.disconnect(signal,slot)
      if not success:
        print("Could not disconnect {signal} to {slot} for {widget}".format(
          signal = signal, slot = slot, widget = widget))
    self.connectionsConnected = False

  def setup(self):
    # Instantiate and connect widgets ...

    # reload button
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "steeredReg Reload"
    self.layout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    #
    # io Collapsible button
    #
    ioCollapsibleButton = ctk.ctkCollapsibleButton()
    ioCollapsibleButton.text = "Volume and Transform Parameters"
    self.layout.addWidget(ioCollapsibleButton)

    # Layout within the parameter collapsible button
    ioFormLayout = qt.QFormLayout(ioCollapsibleButton)

    # InitialTransform node selector
    self.initialTransformSelector = slicer.qMRMLNodeComboBox()
    self.initialTransformSelector.objectName = 'initialTransformSelector'
    self.initialTransformSelector.toolTip = "The initial transform volume."
    self.initialTransformSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.initialTransformSelector.noneEnabled = True
    self.initialTransformSelector.addEnabled = True
    self.initialTransformSelector.removeEnabled = True
    ioFormLayout.addRow("Initial Transform:", self.initialTransformSelector)
    self.initialTransformSelector.setMRMLScene(slicer.mrmlScene)
    self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                        self.initialTransformSelector, 'setMRMLScene(vtkMRMLScene*)')

    # Fixed Volume node selector
    self.fixedSelector = slicer.qMRMLNodeComboBox()
    self.fixedSelector.objectName = 'fixedSelector'
    self.fixedSelector.toolTip = "The fixed volume."
    self.fixedSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.fixedSelector.noneEnabled = False
    self.fixedSelector.addEnabled = False
    self.fixedSelector.removeEnabled = False
    ioFormLayout.addRow("Fixed Volume:", self.fixedSelector)
    self.fixedSelector.setMRMLScene(slicer.mrmlScene)
    self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                        self.fixedSelector, 'setMRMLScene(vtkMRMLScene*)')

    # Moving Volume node selector
    self.movingSelector = slicer.qMRMLNodeComboBox()
    self.movingSelector.objectName = 'movingSelector'
    self.movingSelector.toolTip = "The moving volume."
    self.movingSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.movingSelector.noneEnabled = False
    self.movingSelector.addEnabled = False
    self.movingSelector.removeEnabled = False
    ioFormLayout.addRow("Moving Volume:", self.movingSelector)
    self.movingSelector.setMRMLScene(slicer.mrmlScene)
    self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                        self.movingSelector, 'setMRMLScene(vtkMRMLScene*)')

    # Transform node selector
    self.transformSelector = slicer.qMRMLNodeComboBox()
    self.transformSelector.objectName = 'transformSelector'
    self.transformSelector.toolTip = "The transform volume."
    self.transformSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.transformSelector.noneEnabled = True
    self.transformSelector.addEnabled = True
    self.transformSelector.removeEnabled = True
    ioFormLayout.addRow("Moving To Fixed Transform:", self.transformSelector)
    self.transformSelector.setMRMLScene(slicer.mrmlScene)
    self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                        self.transformSelector, 'setMRMLScene(vtkMRMLScene*)')

    # Output Volume node selector
    self.outputSelector = slicer.qMRMLNodeComboBox()
    self.outputSelector.objectName = 'outputSelector'
    self.outputSelector.toolTip = "The output volume."
    self.outputSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.outputSelector.noneEnabled = True
    self.outputSelector.addEnabled = True
    self.outputSelector.removeEnabled = True
    ioFormLayout.addRow("Output Volume:", self.outputSelector)
    self.outputSelector.setMRMLScene(slicer.mrmlScene)
    self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)',
                        self.outputSelector, 'setMRMLScene(vtkMRMLScene*)')
    
    selectors = (self.fixedSelector, self.movingSelector, self.transformSelector, self.outputSelector, self.initialTransformSelector)
    for selector in selectors:
      selector.connect('currentNodeChanged(vtkMRMLNode*)', self.updateLogicFromGUI)

    #
    # opt Collapsible button
    #
    optCollapsibleButton = ctk.ctkCollapsibleButton()
    optCollapsibleButton.text = "Registration Parameters"
    self.layout.addWidget(optCollapsibleButton)

    # Layout within the parameter collapsible button
    optFormLayout = qt.QFormLayout(optCollapsibleButton)


    # histogram bin slider
    self.histogramBinSlider = ctk.ctkSliderWidget()
    self.histogramBinSlider.decimals = 2
    self.histogramBinSlider.singleStep = 5
    self.histogramBinSlider.minimum = 5
    self.histogramBinSlider.maximum = 500
    self.histogramBinSlider.toolTip = "Number of histogram bins to use for Mattes Mutual Information. Reduce the number of bins if a registration fails. If the number of bins is too large, the estimated PDFs will be a field of impulses and will inhibit reliable registration estimation."
    optFormLayout.addRow("Histogram Bins:", self.histogramBinSlider)

    # spatial sample slider
    self.spatialSampleSlider = ctk.ctkSliderWidget()
    self.spatialSampleSlider.decimals = 2
    self.spatialSampleSlider.singleStep = 1000
    self.spatialSampleSlider.minimum = 1000
    self.spatialSampleSlider.maximum = 10000000
    self.spatialSampleSlider.toolTip = "Number of spatial samples to use in estimating Mattes Mutual Information. Larger values yield more accurate PDFs and improved registration quality."
    optFormLayout.addRow("Spatial Samples:", self.spatialSampleSlider)

    # iteration slider
    self.regIterationSlider = ctk.ctkSliderWidget()
    self.regIterationSlider.decimals = 2
    self.regIterationSlider.singleStep = 10
    self.regIterationSlider.minimum = 10
    self.regIterationSlider.maximum = 10000
    self.regIterationSlider.toolTip = "Number of iterations"
    optFormLayout.addRow("Iterations:", self.regIterationSlider)

    # translation scaling slider
    self.translationScaleSlider = ctk.ctkSliderWidget()
    self.translationScaleSlider.decimals = 2
    self.translationScaleSlider.singleStep = 50.0
    self.translationScaleSlider.minimum = 10.0
    self.translationScaleSlider.maximum = 5000.0
    self.translationScaleSlider.toolTip = "Relative scale of translations to rotations, i.e. a value of 100 means 10mm = 1 degree. (Actual scale used is 1/(TranslationScale^2)). This parameter is used to weight or standardized the transform parameters and their effect on the registration objective function."
    optFormLayout.addRow("Translation Scaling:", self.translationScaleSlider)

    # get default values from logic
    self.histogramBinSlider.value = self.logic.histogramBin
    self.spatialSampleSlider.value = self.logic.spatialSample
    self.regIterationSlider.value = self.logic.regIteration
    self.translationScaleSlider.value = self.logic.translationScale

    #print(self.logic.regIteration)

    sliders = (self.histogramBinSlider, self.spatialSampleSlider, self.regIterationSlider, self.translationScaleSlider)
    for slider in sliders:
      slider.connect('valueChanged(double)', self.updateLogicFromGUI)


    # reg Collapsible button
    regCollapsibleButton = ctk.ctkCollapsibleButton()
    regCollapsibleButton.text = "Registration Selections"
    self.layout.addWidget(regCollapsibleButton)

    # Layout within the parameter collapsible button
    regFormLayout = qt.QFormLayout(regCollapsibleButton)

    self.affinereg = qt.QRadioButton("Affine Registration", regCollapsibleButton)
    self.affinereg.toolTip = "Perform affine registration on 3D volume."
    regCollapsibleButton.layout().addWidget(self.affinereg)

    self.bsplinereg = qt.QRadioButton("Bspline Registration", regCollapsibleButton)
    self.bsplinereg.toolTip = "Perform deformable registration on 3D volume."
    regCollapsibleButton.layout().addWidget(self.bsplinereg)
    

    # Apply button
    self.regButton = qt.QPushButton("Apply")
    self.regButton.toolTip = "Run affine registration."
    #self.regFormLayout.addWidget(self.regButton)
    regFormLayout.addRow(self.regButton)
    self.regButton.connect('clicked(bool)', self.onApply)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Set local var as instance attribute
    #self.regButton = regButton

    regTypes = (self.affinereg, self.bsplinereg)
    for regType in regTypes:
      regType.connect('clicked(bool)', self.updateLogicFromGUI)

    
    # act Collapsible button
    actCollapsibleButton = ctk.ctkCollapsibleButton()
    actCollapsibleButton.text = "Action Selections"
    self.layout.addWidget(actCollapsibleButton)

    # Layout within the parameter collapsible button
    actFormLayout = qt.QFormLayout(actCollapsibleButton)

    self.translation = qt.QRadioButton("Translation", actCollapsibleButton)
    self.translation.toolTip = "Perform translation on 2D slices."
    actCollapsibleButton.layout().addWidget(self.translation)
    self.scaling = qt.QRadioButton("Scaling", actCollapsibleButton)
    self.scaling.setToolTip("Perform scaling on 2D slices.")
    actCollapsibleButton.layout().addWidget(self.scaling)
    
    self.rotation = qt.QRadioButton("Rotation", actCollapsibleButton)
    self.rotation.setToolTip("Perform rotation on 2D slices around center point.")
    actCollapsibleButton.layout().addWidget(self.rotation)

    self.identity = qt.QRadioButton("Identity", actCollapsibleButton)
    self.identity.setToolTip("Reset transform to identity matrix.")
    actCollapsibleButton.layout().addWidget(self.identity)

    
    # Run button
    self.runButton = qt.QPushButton("Interaction")
    self.runButton.toolTip = "Run interaction bot."
    self.runButton.checkable = True
    actFormLayout.addRow(self.runButton)
    self.runButton.connect('toggled(bool)', self.onRunButtonToggled)


    # get default values from logic
    self.translation.checked = self.logic.translation
    self.scaling.checked = self.logic.scaling
    self.rotation.checked = self.logic.rotation
    self.identity.checked = self.logic.identity

    actions = (self.translation, self.scaling, self.rotation, self.identity)
    for action in actions:
      action.connect('clicked(bool)', self.updateLogicFromGUI)
    
    # Add vertical spacer
    self.layout.addStretch(1)

    # to support quicker development:
    import os
    if os.getenv('USERNAME') == '200019959':
      self.logic.testingData()
      self.fixedSelector.setCurrentNode(slicer.util.getNode('MRHead*'))
      self.movingSelector.setCurrentNode(slicer.util.getNode('neutral*'))
      self.transformSelector.setCurrentNode(slicer.util.getNode('movingToFixed*'))
      self.initialTransformSelector.setCurrentNode(slicer.util.getNode('movingToFixed*'))


  def updateLogicFromGUI(self,args):
    self.logic.fixed = self.fixedSelector.currentNode()
    self.logic.moving = self.movingSelector.currentNode()
    self.logic.transform = self.transformSelector.currentNode()
    
    self.logic.histogramBin = self.histogramBinSlider.value
    self.logic.spatialSample = self.spatialSampleSlider.value
    self.logic.regIteration = self.regIterationSlider.value
    self.logic.translationScale = self.translationScaleSlider.value

    self.logic.translation = self.translation.checked
    self.logic.scaling = self.scaling.checked
    self.logic.rotation = self.rotation.checked
    self.logic.identity = self.identity.checked

    self.logic.interaction = self.interaction
  
    if self.identity.checked:
      self.logic.actionState = "identity"
      m = self.logic.transform.GetMatrixTransformToParent()
      for i in range(4):
        for j in range(4):
          m.SetElement(i,j, self.logic.identityMatrix[i][j])
          
   
  def onApply(self):
    fixedVolume = self.fixedSelector.currentNode()
    movingVolume = self.movingSelector.currentNode()
    #outputVolume = self.outputSelector.currentNode()
    initialTransform = self.initialTransformSelector.currentNode()
    outputTransform = self.transformSelector.currentNode()

    self.parameters = {}
    self.parameters['InitialTransform'] = initialTransform.GetID()
    self.parameters['FixedImageFileName'] = fixedVolume.GetID()
    self.parameters['MovingImageFileName'] = movingVolume.GetID()
    self.parameters['OutputTransform'] = outputTransform.GetID()
    #self.parameters['ResampledImageFileName'] = outputVolume.GetID()

    
    self.parameters['Iterations']=self.regIterationSlider.value

    print('registration begin')
    print "return result every %d iterations" %(self.regIterationSlider.value)
    
    for regRound in xrange(2):       
      print "round %d" %(regRound)
      self.affineregModel()
      
      m = self.logic.transform.GetMatrixTransformToParent()
        
      H = [[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
      for i in range(4):
        for j in range(4):
          H[i][j] = m.GetElement(i,j)
        print "[%8.2f %8.2f %8.2f %8.2f]" %(H[i][0], H[i][1], H[i][2], H[i][3])
        
    print('registration done')


  def affineregModel(self):
    print('registering')
    return (slicer.cli.run( slicer.modules.affineregistration, None,
                            self.parameters, wait_for_completion=True) )

    #########################################################################
      
  def onRunButtonToggled(self, checked):
    if checked:
      #print(checked)
      self.logic.interaction=True
      self.logic.start()
      self.runButton.text = "Stop"
    else:
      #print(checked)
      self.logic.interaction=False
      self.logic.stop()
      self.runButton.text = "Interact"

  def onReload(self,moduleName="steeredReg"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()

#
# steeredReg logic
#

class steeredRegLogic(object):
  """ Implement a template matching optimizer that is
  integrated with the slicer main loop.
  Note: currently depends on numpy/scipy installation in mac system
  """

  def __init__(self,fixed=None,moving=None,transform=None):
    self.interval = 20
    self.timer = None

    # parameter defaults
    self.histogramBin = 30
    self.spatialSample = 10000
    self.regIteration = 50
    self.translationScale = 100.0

    self.translation = False
    self.scaling = False
    self.rotation = False
    self.identity = False

    # slicer nodes set by the GUI
    self.fixed = fixed
    self.moving = moving
    self.transform = transform

    # optimizer state variables
    self.iteration = 0
    self.interaction = False

    self.position = []
    self.paintCoordinates = []

    self.lastEventPosition = [0.0, 0.0, 0.0]
    self.startEventPosition = [0.0, 0.0, 0.0]

    self.rasCenter = [0.0, 0.0, 0.0]
    self.lastVec = [0.0, 0.0, 0.0]
    self.lastVecTheta = [0.0, 0.0, 0.0]

    self.translateDist = [0.0, 0.0, 0.0]
    self.scaleFactor = [1.0, 1.0, 1.0]
    self.rotateAngle = [0.0, 0.0, 0.0]

    self.identityMatrix = [[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
          
    print("Hello")
    
    self.actionState = "idle"
    self.interactorObserverTags = []
    
    self.styleObserverTags = []
    self.sliceWidgetsPerStyle = {}

    self.nodeIndexPerStyle = {}
    self.sliceNodePerStyle = {}

  def start(self):

    #print(self.identity)            
    self.removeObservers()
    # get new slice nodes
    layoutManager = slicer.app.layoutManager()
    sliceNodeCount = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    for nodeIndex in xrange(sliceNodeCount):
      # find the widget for each node in scene
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(nodeIndex, 'vtkMRMLSliceNode')
      sliceWidget = layoutManager.sliceWidget(sliceNode.GetLayoutName())
      
      if sliceWidget:
          
        # add obserservers and keep track of tags
        style = sliceWidget.sliceView().interactorStyle()
        self.interactor = style.GetInteractor()
        self.sliceWidgetsPerStyle[self.interactor] = sliceWidget
        self.nodeIndexPerStyle[self.interactor] = nodeIndex
        self.sliceNodePerStyle[self.interactor] = sliceNode
        
        events = ("LeftButtonPressEvent","LeftButtonReleaseEvent","MouseMoveEvent", "KeyPressEvent","EnterEvent", "LeaveEvent")
        for event in events:
          tag = self.interactor.AddObserver(event, self.processEvent, 1.0)
          self.interactorObserverTags.append(tag)
          


  def processEvent(self,observee,event=None):

      
    if self.sliceWidgetsPerStyle.has_key(observee):
      sliceWidget = self.sliceWidgetsPerStyle[observee]
      style = sliceWidget.sliceView().interactorStyle()
      self.interactor = style.GetInteractor()
      nodeIndex = self.nodeIndexPerStyle[observee]
      sliceNode = self.sliceNodePerStyle[observee]


      windowSize = sliceNode.GetDimensions()
      windowW = windowSize[0]
      windowH = windowSize[1]

                                
      if event == "LeftButtonPressEvent":
        xy = style.GetInteractor().GetEventPosition()
        xyz = sliceWidget.sliceView().convertDeviceToXYZ(xy)
        ras = sliceWidget.sliceView().convertXYZToRAS(xyz)
        self.lastEventPosition = ras
        self.startEventPosition = ras
        if self.translation:
          self.actionState = "translationON"
          self.translateDist = [0.0, 0.0, 0.0]
          
        elif self.scaling:
          self.actionState = "scalingON"
          self.scaleFactor = [1.0, 1.0, 1.0]
          
        elif self.rotation:
          self.actionState = "rotationON"
          self.rotateAngle = [0.0, 0.0, 0.0]
          
          xyCenter = [0.0, 0.0, 0.0];
          xyCenter[0] = windowSize[0]/2.0;
          xyCenter[1] = windowSize[1]/2.0;
          xyzCenter = sliceWidget.sliceView().convertDeviceToXYZ( xyCenter );
          self.rasCenter = sliceWidget.sliceView().convertXYZToRAS( xyzCenter );
    
          self.lastVec[0]=(self.lastEventPosition[0]-self.rasCenter[0]);
          self.lastVec[1]=(self.lastEventPosition[1]-self.rasCenter[1]);
          self.lastVec[2]=(self.lastEventPosition[2]-self.rasCenter[2]);

          if self.lastVec[2] == 0:
            xa=self.lastVec[0];
            ya=self.lastVec[1];
            a=sqrt(xa*xa+ya*ya);       
            ac=-xa;
            theta=acos(ac/a);
            if ya<0:
              theta=2*pi-theta        
            self.lastVecTheta[2]=theta;

          elif self.lastVec[0] == 0:
            xa=self.lastVec[1];
            ya=self.lastVec[2];
            a=sqrt(xa*xa+ya*ya);       
            ac=-xa;
            theta=acos(ac/a);
            if ya<0:
              theta=2*pi-theta        
            self.lastVecTheta[0]=theta;

          elif self.lastVec[1] == 0:
            xa=self.lastVec[0];
            ya=self.lastVec[2];
            a=sqrt(xa*xa+ya*ya);       
            ac=-xa;
            theta=acos(ac/a);
            if ya<0:
              theta=2*pi-theta        
            self.lastVecTheta[1]=theta;

          else:
            pass

        else:
            pass

        #print(self.actionState)
        self.abortEvent(event)

      elif event == "LeftButtonReleaseEvent":
        if self.actionState == "translationON":
          self.actionState = "translation"
          print "Translate distance this time = (%.2f %.2f %.2f)" %(self.translateDist[0], self.translateDist[1], self.translateDist[2])
          
        elif self.actionState == "scalingON":
          self.actionState = "scaling"
          print "Scale factor this time = (%.2f %.2f %.2f)" %(self.scaleFactor[0], self.scaleFactor[1], self.scaleFactor[2])
          
        elif self.actionState == "rotationON":
          self.actionState = "rotation"
          print "Rotate Angle this time = (%.2f %.2f %.2f)" %(self.rotateAngle[0]/pi*180.0, self.rotateAngle[1]/pi*180.0, self.rotateAngle[2]/pi*180.0)
        else:
          pass

        #print(self.actionState)
        self.abortEvent(event)
        
          
      elif event == "MouseMoveEvent":

        #print(self.actionState)

        xy = style.GetInteractor().GetEventPosition()
        xyz = sliceWidget.sliceView().convertDeviceToXYZ(xy);
        ras = sliceWidget.sliceView().convertXYZToRAS(xyz)
        currentEventPosition = ras

        m = self.transform.GetMatrixTransformToParent()
        
        H1 = [[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
        H2 = [[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
        H21 = [[1.0,0.0,0.0,0.0],[0.0,1.0,0.0,0.0],[0.0,0.0,1.0,0.0],[0.0,0.0,0.0,1.0]]
        for i in range(4):
          for j in range(4):
            H1[i][j] = m.GetElement(i,j)
        

        if self.actionState == "translationON":

          delta = [0.0, 0.0, 0.0]

          for i in range(3):
            delta[i] = currentEventPosition[i]-self.lastEventPosition[i]
            self.translateDist[i] = self.translateDist[i]+delta[i]
            m.SetElement(i,3, m.GetElement(i,3)+delta[i])         
            

          self.lastEventPosition=currentEventPosition            
          self.abortEvent(event)

        elif self.actionState == "scalingON":

          delta = [0.0, 0.0, 0.0]
          percent = [1.0, 1.0, 1.0]
          
          for i in range(3):
            delta[i] = -(currentEventPosition[i]-self.lastEventPosition[i])
            
          if nodeIndex == 0:
            p = 0
            q = 1                                  
          elif nodeIndex == 1:
            p = 1
            q = 2
          elif nodeIndex == 2:
            p = 0
            q = 2
          else:
            pass

          percent[p] = (windowW + delta[p])/(1.0*windowW);
          percent[q] = (windowH + delta[q])/(1.0*windowH);          
          self.scaleFactor[p] = self.scaleFactor[p]*percent[p]
          self.scaleFactor[q] = self.scaleFactor[q]*percent[q]

          H2[p][p] = percent[p]
          H2[q][q] = percent[q]

          for i in range(4):
            for j in range(4):
              tmp=0
              for k in range(4):
                tmp=tmp+H2[i][k]*H1[k][j]

              H21[i][j]=tmp

          for i in range(4):
            for j in range(4):
              m.SetElement(i,j,H21[i][j]) 

          self.lastEventPosition=currentEventPosition
          self.abortEvent(event)

          

        elif self.actionState == "rotationON":
          
          if currentEventPosition[0] != self.lastEventPosition[0] or currentEventPosition[1] != self.lastEventPosition[1] or currentEventPosition[2] != self.lastEventPosition[2]:

            currentVec=[0.0, 0.0, 0.0]
            for i in range(3):
              currentVec[i]=currentEventPosition[i]-self.rasCenter[i];

            currentVecTheta=[0.0, 0.0, 0.0]
              
            if currentVec[2] == 0:
              axisID = 2
              p = 0
              q = 1
                          
            elif currentVec[0] == 0:
              axisID = 0
              p = 1
              q = 2
              
            elif currentVec[1] == 0:
              axisID = 1
              p = 0
              q = 2                       
            else:
              pass

            xb=currentVec[p];
            yb=currentVec[q];
            b=sqrt(xb*xb+yb*yb);                   

            bc=-xb;
            currentVecTheta[axisID]=acos(bc/b);
            if yb<0:
              currentVecTheta[axisID]=2*pi-currentVecTheta[axisID]
            
            deltaTheta=self.lastVecTheta[axisID]-currentVecTheta[axisID]
            if self.lastVecTheta[axisID]>=0 and self.lastVecTheta[axisID]<pi/2.0 and currentVecTheta[axisID]>=pi*1.5 and currentVecTheta[axisID]<pi*2.0:
              deltaTheta=deltaTheta+2.0*pi;
            elif self.lastVecTheta[axisID]>=pi*1.5 and self.lastVecTheta[axisID]<pi*2.0 and currentVecTheta[axisID]>=0 and currentVecTheta[axisID]<pi/2.0:
              deltaTheta=deltaTheta-2.0*pi;
            else:
              pass              
            self.rotateAngle[axisID] = self.rotateAngle[axisID]+deltaTheta;
            
            ccos=cos(deltaTheta);
            ssin=sin(deltaTheta);

            H2[p][p]=ccos
            H2[p][q]=-ssin
            H2[q][p]=ssin
            H2[q][q]=ccos

            self.lastVec=currentVec
            self.lastVecTheta=currentVecTheta;

            for i in range(4):
              for j in range(4):
                tmp=0
                for k in range(4):
                  tmp=tmp+H2[i][k]*H1[k][j];

                H21[i][j]=tmp

            for i in range(4):
              for j in range(4):
                m.SetElement(i,j,H21[i][j]) 

          self.lastEventPosition=currentEventPosition
          self.abortEvent(event)

        else:
          pass
          
      else:
        pass




  def stop(self):
    self.actionState = "idle"
    self.removeObservers()
    

  def removeObservers(self):
    # remove observers and reset
    for tag in self.interactorObserverTags:
      self.interactor.RemoveObserver(tag)
    self.interactorObserverTags = []
    self.sliceWidgetsPerStyle = {}
    

  def abortEvent(self,event):
    """Set the AbortFlag on the vtkCommand associated 
    with the event - causes other things listening to the 
    interactor not to receive the events"""
    # TODO: make interactorObserverTags a map to we can 
    # explicitly abort just the event we handled - it will
    # be slightly more efficient
    for tag in self.interactorObserverTags:
      cmd = self.interactor.GetCommand(tag)
      cmd.SetAbortFlag(1)


  def testingData(self):
    """Load some default data for development
    and set up a transform and viewing scenario for it.
    """
    if not slicer.util.getNodes('MRHead*'):
      import os
      fileName = "C:\Projects\NAMIC\data\MR-head.nrrd"
      vl = slicer.modules.volumes.logic()
      volumeNode = vl.AddArchetypeVolume(fileName, "MRHead", 0)
    if not slicer.util.getNodes('neutral*'):
      import os
      fileName = "C:\Projects\NAMIC\data\spgr.nrrd"
      vl = slicer.modules.volumes.logic()
      volumeNode = vl.AddArchetypeVolume(fileName, "neutral", 0)
    if not slicer.util.getNodes('movingToFixed'):
      # Create transform node
      transform = slicer.vtkMRMLLinearTransformNode()
      transform.SetName('movingToFixed')
      slicer.mrmlScene.AddNode(transform)
    head = slicer.util.getNode('MRHead')
    neutral = slicer.util.getNode('neutral')
    transform = slicer.util.getNode('movingToFixed')
    ###
    neutral.SetAndObserveTransformNodeID(transform.GetID())
    ###
    compositeNodes = slicer.util.getNodes('vtkMRMLSliceCompositeNode*')
    for compositeNode in compositeNodes.values():
      compositeNode.SetBackgroundVolumeID(head.GetID())
      compositeNode.SetForegroundVolumeID(neutral.GetID())
      compositeNode.SetForegroundOpacity(0.5)
    applicationLogic = slicer.app.applicationLogic()
    applicationLogic.FitSliceToAll()


    



