import Rhino
import System.Drawing
import math

def blendChannel(a, b, amount):
    return a + (b - a) * amount

def blendColors(a, b, amount):
    A = blendChannel(a.A, b.A, amount)
    R = blendChannel(a.R, b.R, amount)
    G = blendChannel(a.G, b.G, amount)
    B = blendChannel(a.B, b.B, amount)
    result = System.Drawing.Color.FromArgb(A, R, G, B)
    return result

def setBrightness(inputColor, value):
    hsb = ColorHsb(inputColor)
    hsb.B = value
    return hsb.ToRgba()

def setSaturation(inputColor, value):
    hsb = ColorHsb(inputColor)
    hsb.S = value
    return hsb.ToRgba()

def getTint(inputColor, amount=0.5):
    white = System.Drawing.Color.FromArgb(inputColor.A, 255, 255, 255)
    return blendColors(inputColor, white, amount)

def getShade(inputColor, amount=0.5):
    black = System.Drawing.Color.FromArgb(inputColor.A, 0, 0, 0)
    return blendColors(inputColor, black, amount)


class ColorHsb(object):
    def __init__(self, color=None):
        if color:
            self.color = color
            self.A = color.A
            self.H = color.GetHue()
            self.S = color.GetSaturation()
            self.B = color.GetBrightness()
        else:
            self.color = None
            self.A = 255
            self.H = 0
            self.S = 0.5
            self.B = 0.5

    def ToRgba(self):
        a = self.A
        h = self.H
        s = self.S
        b = self.B
        
        if (0 > a or 255 < a):
            raise ValueError("invalid alpha value")
        if (0.0 > h or 360.0 < h):
            raise ValueError("invalid hue value")
        if (0.0 > s or 1.0 < s):
            raise ValueError("invalid saturation value")
        if (0.0 > b or 1.0 < b):
            raise ValueError("invalid brightness value")
        if (0 == s):
            return System.Drawing.Color.FromArgb(a, int(b * 255), int(b * 255), int(b * 255))
        
        fMax = fMid = fMin = 0.0
        iSextant = iMax = iMid = iMin = 0
        if (0.5 < b):
            fMax = b - (b * s) + s
            fMin = b + (b * s) - s
        else:
            fMax = b + (b * s)
            fMin = b - (b * s)
        
        iSextant = int(math.floor(h / 60))
        if (300 <= h):
            h -= 360.0
        h /= 60.0
        h -= 2.0 * float(math.floor(((iSextant + 1.0) % 6.0) / 2.0))
        if (0 == iSextant % 2):
            fMid = h * (fMax - fMin) + fMin
        else:
            fMid = fMin - h * (fMax - fMin)
        iMax = int(fMax * 255)
        iMid = int(fMid * 255)
        iMin = int(fMin * 255)
        if iSextant == 1: 
            return System.Drawing.Color.FromArgb(a, iMid, iMax, iMin)
        elif iSextant == 2:
            return System.Drawing.Color.FromArgb(a, iMin, iMax, iMid)
        elif iSextant == 3: 
            return System.Drawing.Color.FromArgb(a, iMin, iMid, iMax)
        elif iSextant == 4:
            return System.Drawing.Color.FromArgb(a, iMid, iMin, iMax)
        elif iSextant == 5: 
            return System.Drawing.Color.FromArgb(a, iMax, iMin, iMid)
        else: 
            return System.Drawing.Color.FromArgb(a, iMax, iMid, iMin)

class UiColor(object):
    def __init__(self, name):
        self._name = name
        
    def get(self):
        return getattr(Rhino.ApplicationSettings.AppearanceSettings, self._name)
        
    def set(self, value):
        setattr(Rhino.ApplicationSettings.AppearanceSettings, self._name, value)
        
    def getDefault(self):
        return getattr(Rhino.ApplicationSettings.AppearanceSettings.GetDefaultState(), self._name)
        
    def restoreDefault(self):
        self.set(self.getDefault())
        
    @property
    def name(self):
        return 'Rhino.ApplicationSettings.AppearanceSettings.' + self._name
        
    @name.setter
    def name(self, val):
        self._name = val


class UiPaintColor(UiColor):
    def __init__(self, colorIndex):
        if isinstance(colorIndex, basestring):
            self._name = 'Rhino.ApplicationSettings.PaintColor.' + colorIndex
            value = System.Enum.Parse(Rhino.ApplicationSettings.PaintColor, colorIndex)
            self.colorIndex = value
        else:
            self._name = "Unknown"
            self.colorIndex = colorIndex
        
    def get(self):
        return Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(self.colorIndex)
    
    def set(self, value):
        Rhino.ApplicationSettings.AppearanceSettings.SetPaintColor(self.colorIndex, value, True)
    
    def getDefault(self):
        return Rhino.ApplicationSettings.AppearanceSettings.DefaultPaintColor(self.colorIndex)

    @property
    def name(self):
        return self._name

class ColorGroup(list):
    def set(self, value):
        for item in self:
            item.set(value)

    
def setDarkScheme(baseColor, accentColor):
    colorfunc = getTint
    
    nonclient = baseColor
    client = colorfunc(baseColor, 0.2)
    base_color_group.set(client)
    textbox_color_group.set(client)
    ui_color_group.set(nonclient)
    cHover = setSaturation(setBrightness(blendColors(accentColor, baseColor, 0.3), 0.6), 0.4)
    ui_hover_group.set(cHover)
    ui_click_group.set(accentColor)
    ui_text_group.set(colorfunc(baseColor, 0.9))
    ui_border_group.set(colorfunc(baseColor, 0.4))
    new_object_group.set(System.Drawing.Color.FromArgb(255, 255, 255, 255))
 
    # viewports
    vpGridMajor.set(colorfunc(client, 0.1))
    vpGridMinor.set(colorfunc(client, 0.05))
    viewport_accent_group.set(colorfunc(client, 0.2))
    cl = colorfunc(baseColor, 0.4)
    vpGridX.set(blendColors(System.Drawing.Color.FromArgb(255, 255, 0, 0), baseColor, 0.5))
    vpGridY.set(blendColors(System.Drawing.Color.FromArgb(255, 0, 155, 45), baseColor, 0.5))
    vpGridZ.set(blendColors(System.Drawing.Color.FromArgb(255, 0, 0, 255), baseColor, 0.5))
    vpActiveTitleBackground.set(accentColor)
    
    activeCaption.set(blendColors(baseColor, accentColor, 0.7))
    inactiveCaption.set(blendColors(baseColor, accentColor, 0.2))

def setLightScheme(baseColor, accentColor):
    colorfunc = getTint
    
    base_color_group.set(baseColor)
    textbox_color_group.set(System.Drawing.Color.White)
    colorUi = colorfunc(baseColor, 0.6)
    ui_color_group.set(colorfunc(baseColor, 0.6))
    cHover = setSaturation(setBrightness(blendColors(accentColor, baseColor, 0.3), 0.6), 0.4)
    ui_hover_group.set(cHover)
    ui_click_group.set(accentColor)
    ui_text_group.set(getShade(baseColor, 0.8))
    ui_border_group.set(getShade(colorUi, 0.25))
    new_object_group.set(System.Drawing.Color.FromArgb(255, 0, 0, 0))

    # viewports
    vpGridMajor.set(getTint(baseColor, 0.1))
    vpGridMinor.set(getTint(baseColor, 0.05))
    viewport_accent_group.set(getShade(baseColor, 0.2))
    cl = getTint(baseColor, 0.2)
    vpGridX.set(blendColors(System.Drawing.Color.FromArgb(255, 255, 0, 0), baseColor, 0.5))
    vpGridY.set(blendColors(System.Drawing.Color.FromArgb(255, 0, 155, 45), baseColor, 0.5))
    vpGridZ.set(blendColors(System.Drawing.Color.FromArgb(255, 0, 0, 255), baseColor, 0.5))
    vpActiveTitleBackground.set(accentColor)

    activeCaption.set(blendColors(baseColor, accentColor, 0.7))
    inactiveCaption.set(blendColors(baseColor, accentColor, 0.2))


def setAllColorsSame(color):
    colorCount = 0
    for c in System.Enum.GetValues(Rhino.ApplicationSettings.PaintColor):
        o = UiPaintColor(c)
        o.set(color)
        colorCount += 1
    
    for field in dir(Rhino.ApplicationSettings.AppearanceSettings):
        try:
            setattr(Rhino.ApplicationSettings.AppearanceSettings, field, color)
            colorCount += 1
        except:
            pass
    
    print colorCount
            
def setRandomColors():
    def nextColor():
        for H in range(0, 360, 10):
            for S in range(75, 100, 25):
                for B in range(30, 70, 10):
                    c = ColorHsb()
                    c.H = H
                    c.S = S / 100.0
                    c.B = B / 100.0
                    yield c.ToRgba()

    colors = nextColor()

    for c in System.Enum.GetValues(Rhino.ApplicationSettings.PaintColor):
        o = UiPaintColor(c)
        o.set(next(colors))
    for field in dir(Rhino.ApplicationSettings.AppearanceSettings):
        try:
            setattr(Rhino.ApplicationSettings.AppearanceSettings, field, next(colors))
            colorCount += 1
        except:
            pass

def restoreDefaults():
    for color in all_colors:
        color.restoreDefault()

def isolateUiColor(indexToHighlight):
    for i, c in enumerate(all_colors):
        defaultColor = c.getDefault()
        if i == indexToHighlight:
            print(c.name)
            defaultColor = System.Drawing.Color.FromArgb(255, 0, 0, 255)
        else:
            defaultColor = getTint(defaultColor, .8)
        c.set(defaultColor)
    # commandPromptText.set(System.Drawing.Color(FromArgb(255, 120, 120, 120)))

# Init colors
panel = UiPaintColor('PanelBackground')
activeTabTop = UiPaintColor('NormalStart')
activeTabBottom = UiPaintColor('NormalEnd')
inactiveTabTop = UiPaintColor('HotStart')
inactiveTabBottom = UiPaintColor('HotEnd')
border = UiPaintColor('NormalBorder')
buttonHoverBorder = UiPaintColor('MouseOverControlBorder')
buttonHoverTop = UiPaintColor('MouseOverControlStart')
buttonHoverBottom = UiPaintColor('MouseOverControlEnd')
buttonClickTop = UiPaintColor('PressedStart')
buttonClickBottom = UiPaintColor('PressedEnd')
dialogText = UiPaintColor('TextEnabled')
disabledText = UiPaintColor('TextDisabled')
newLayer = UiColor('DefaultLayerColor')
newObject = UiColor('DefaultObjectColor')
commandPromptBackground = UiColor('CommandPromptBackgroundColor')
commandPromptText = UiColor('CommandPromptTextColor')
vpBackground = UiColor('ViewportBackgroundColor')
vpGridMajor = UiColor('GridThickLineColor')
vpGridMinor = UiColor('GridThinLineColor')
vpGridX = UiColor('GridXAxisLineColor')
vpGridY = UiColor('GridYAxisLineColor')
vpGridZ = UiColor('GridZAxisLineColor')

crosshair = UiColor('CrosshairColor')
defaultLayer = UiColor('DefaultLayerColor')
editCandidate = UiColor('EditCandidateColor')
feedback = UiColor('FeedbackColor')
frameBackground = UiColor('FrameBackgroundColor')
lockedObject = UiColor('LockedObjectColor')
pageViewPaperColor = UiColor('PageviewPaperColor')
selectedObject = UiColor('SelectedObjectColor')
trackingColor = UiColor('TrackingColor')
editBoxBackground = UiPaintColor('EditBoxBackground')

var = Rhino.ApplicationSettings.AppearanceSettings.DefaultLayerColor
v2 = Rhino.ApplicationSettings.PaintColor.TextDisabled

worldAxesX = UiColor('WorldCoordIconXAxisColor')
worldAxesY = UiColor('WorldCoordIconYAxisColor')
worldAxesZ = UiColor('WorldCoordIconZAxisColor')

vpActiveTitleBackground = UiPaintColor('ActiveViewportTitle')
vpInactiveTitleBackground = UiPaintColor('InactiveViewportTitle')
activeCaption = UiPaintColor('ActiveCaption')
inactiveCaption = UiPaintColor('InactiveCaption')

base_color_group = ColorGroup([
    vpBackground, 
    commandPromptBackground,
    editBoxBackground,
    ]
)
textbox_color_group = ColorGroup([
    commandPromptBackground,
    editBoxBackground,
    ]
)
ui_color_group = ColorGroup([
    panel,
    activeTabTop,
    activeTabBottom,
    inactiveTabTop,
    inactiveTabBottom,
    pageViewPaperColor,
    activeCaption,
    inactiveCaption
    ]
)
ui_text_group = ColorGroup([
    commandPromptText,
    dialogText,
    ]
)
ui_hover_group = ColorGroup([
    buttonHoverTop,
    buttonHoverBottom,
    ]
)
ui_click_group = ColorGroup([
    buttonClickTop,
    buttonClickBottom,
    ]
)
ui_border_group = ColorGroup([
    border,
    vpInactiveTitleBackground,
    disabledText,
    buttonHoverBorder,
])
viewport_accent_group = ColorGroup([
    worldAxesX,
    worldAxesY,
    worldAxesZ,
    lockedObject,
])
new_object_group = ColorGroup([
    newLayer,
    newObject
])
other_colors_group = ColorGroup([
    vpGridMajor,
    vpGridMinor,
    vpGridX,
    vpGridY,
    vpGridZ,
    crosshair,
    defaultLayer,
    editCandidate,
    feedback,
    frameBackground,
    selectedObject,
    trackingColor,
    vpActiveTitleBackground,
    vpInactiveTitleBackground,
])

all_colors = []
all_colors.extend(base_color_group)
all_colors.extend(ui_color_group)
all_colors.extend(ui_text_group)
all_colors.extend(ui_hover_group)
all_colors.extend(ui_click_group)
all_colors.extend(ui_border_group)
all_colors.extend(viewport_accent_group)
all_colors.extend(new_object_group)
all_colors.extend(other_colors_group)

i = 200
darkGreen = System.Drawing.Color.FromArgb(255, 40, 40, 30)
darkBlue = System.Drawing.Color.FromArgb(255, 30, 40, 60)
darkDarkBlue = System.Drawing.Color.FromArgb(255, 10, 20, 30)
mediumBlue = System.Drawing.Color.FromArgb(255, 60, 70, 100)
darkGray = System.Drawing.Color.FromArgb(255, 30, 30, 30)
mediumGrayBlue = System.Drawing.Color.FromArgb(255, 70, 70, 90)

lightGray = System.Drawing.Color.FromArgb(255, 185, 185, 200)
lightLightGray = System.Drawing.Color.FromArgb(255, 235, 235, 255)

defaultGray = System.Drawing.Color.FromArgb(255, 157, 163, 170)

accentBlue = System.Drawing.Color.FromArgb(128, 200, 255)
accentOrange = System.Drawing.Color.FromArgb(255, 128, 0)
accentIceBlue = System.Drawing.Color.FromArgb(200, 245, 255)

def detectMode():
    isDefault = True
    for c in all_colors:
        if c.name == 'Rhino.ApplicationSettings.PaintColor.EditBoxBackground':
            continue
        if c.get() != c.getDefault():
            print "Not default: " + c.name
            isDefault = False
    
    if isDefault:
        return 0
        
    if ColorHsb(vpBackground.get()).B > ColorHsb(panel.get()).B:
        return 1
    
    return 2

def run():
    go = Rhino.Input.Custom.GetOption()
    schemeType = detectMode()
    go.SetCommandPrompt("Scheme Settings")
    go.AddOptionList("Type", ["Default", "Dark", "Light"], schemeType)

    if schemeType == 1: # Dark mode    
        defaultBaseColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.NormalEnd)
        defaultAccentColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.PressedEnd)
    else:
        defaultBaseColor = Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor # System.Drawing.Color.FromArgb(255, 60, 70, 100)
        defaultAccentColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.PressedEnd)

    baseColorOption = Rhino.Input.Custom.OptionColor(defaultBaseColor)
    accentColorOption = Rhino.Input.Custom.OptionColor(defaultAccentColor)
    go.AddOptionColor("BaseColor", baseColorOption, "Base Color")
    go.AddOptionColor("AccentColor", accentColorOption, "Accent Color")
    go.AcceptNothing(True)
    
    while True:
        result = go.Get()
        if result == Rhino.Input.GetResult.Option:
            n = go.Option().EnglishName
            if n == 'Type':
                schemeType = go.Option().CurrentListOptionIndex
        elif result == Rhino.Input.GetResult.Nothing:
            print "Success!!!"
            break
        else:
            return
            
    print schemeType
    if schemeType == 0:
        restoreDefaults()
    elif schemeType == 1:
        setDarkScheme(baseColorOption.CurrentValue, accentColorOption.CurrentValue)
    elif schemeType == 2:
        setLightScheme(baseColorOption.CurrentValue, accentColorOption.CurrentValue)

def run2():
    go = Rhino.Input.Custom.GetOption()
    schemeType = detectMode()

    if schemeType == 1: # Dark mode    
        defaultBaseColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.NormalEnd)
        defaultAccentColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.PressedEnd)
    else:
        defaultBaseColor = Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor # System.Drawing.Color.FromArgb(255, 60, 70, 100)
        defaultAccentColor = Rhino.ApplicationSettings.AppearanceSettings.GetPaintColor(Rhino.ApplicationSettings.PaintColor.PressedEnd)

    go.SetCommandPrompt("Scheme Type")
    if schemeType == 0:
        go.SetCommandPromptDefault("Default")
    elif schemeType == 1:
        go.SetCommandPromptDefault("Dark")
    elif schemeType == 2:
        go.SetCommandPromptDefault("Light")
    go.AddOption("Dark")
    go.AddOption("Light")
    go.AddOption("RestoreDefaults")
    go.AcceptNothing(True)

    result = go.Get()
    if result == Rhino.Input.GetResult.Option:
        n = go.Option().EnglishName
        if n == 'RestoreDefaults':
            restoreDefaults()
            return
        elif n == "Dark":
            schemeType = 1
        elif n == "Light":
            schemeType = 2
    elif result == Rhino.Input.GetResult.Nothing:
        pass
    else:
        return
        
    if schemeType == 0:
        print "Retaining default scheme."
        return

    go = Rhino.Input.Custom.GetOption()
    go.SetCommandPrompt("Set colors, press Enter when done")
    baseColorOption = Rhino.Input.Custom.OptionColor(defaultBaseColor)
    accentColorOption = Rhino.Input.Custom.OptionColor(defaultAccentColor)
    go.AddOptionColor("BaseColor", baseColorOption, "Base Color")
    go.AddOptionColor("AccentColor", accentColorOption, "Accent Color")
    go.AcceptNothing(True)
    
    while(True):
        result = go.Get()
        if result == Rhino.Input.GetResult.Option:
            n = go.Option().EnglishName
            if n == 'Type':
                schemeType = go.Option().CurrentListOptionIndex
        elif result == Rhino.Input.GetResult.Nothing:
            break
        else:
            return

    print schemeType
    if schemeType == 0:
        restoreDefaults()
    elif schemeType == 1:
        setDarkScheme(baseColorOption.CurrentValue, accentColorOption.CurrentValue)
    elif schemeType == 2:
        setLightScheme(baseColorOption.CurrentValue, accentColorOption.CurrentValue)


run2()


# 
# setDarkScheme(mediumBlue, accentBlue)
# setLightScheme(lightLightGray, accentBlue)
# Rhino.ApplicationSettings.AppearanceSettings.SetPaintColor(Rhino.ApplicationSettings.PaintColor.TextDisabled, System.Drawing.Color.GreenYellow)
# setAllColorsSame(darkDarkBlue)
# restoreDefaults()
# setRandomColors()
# isolateUiColor(39)
# Rhino.ApplicationSettings.AppearanceSettings.ViewportBackgroundColor = baseColor