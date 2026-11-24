; BÖRÜ yükleyicisi (Inno Setup 6). Derleme: kurulum_derle.bat ya da ISCC.exe boru.iss
; Yönetici izni istemez: kullanıcının kendi klasörüne kurar (%LOCALAPPDATA%\Programs\BORU).
; Kullanıcı verisi (Belgeler\BORU) ve Claude Code / Codex ayarları kaldırmada SİLİNMEZ.

#define Ad "BÖRÜ"
#define Surum "0.6.2"
#define Yayinci "DownStroke Studios"
#define Exe "BORU.exe"

[Setup]
AppId={{8A9AB666-4CF3-44E3-97E5-2676F0F18858}
AppName={#Ad}
AppVersion={#Surum}
AppVerName={#Ad} {#Surum}
AppPublisher={#Yayinci}
VersionInfoVersion=0.6.2.0
VersionInfoDescription={#Ad} yükleyicisi
DefaultDirName={autopf}\BORU
DefaultGroupName={#Ad}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
DisableWelcomePage=no
WizardSizePercent=110
WizardImageFile=sol_100.bmp,sol_150.bmp,sol_200.bmp
WizardSmallImageFile=kucuk_100.bmp,kucuk_150.bmp,kucuk_200.bmp
WizardImageStretch=no
WizardImageBackColor=$420F0B
SetupIconFile=..\boru.ico
UninstallDisplayIcon={app}\{#Exe}
UninstallDisplayName={#Ad} {#Surum}
OutputDir=cikti
OutputBaseFilename=BORU_Kurulum_{#Surum}
Compression=lzma2/ultra64
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

[Languages]
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"; InfoBeforeFile: "bilgi_tr.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; InfoBeforeFile: "bilgi_en.txt"

[Messages]
tr.WelcomeLabel1=BÖRÜ'ye hoş geldin
tr.WelcomeLabel2=BÖRÜ, yapay zekâyla (Claude Code, Codex) oyun ve proje geliştirirken masaüstünde seni ve projeni kollayan detaycı bir kurttur.%n%nBu sihirbaz BÖRÜ {#Surum} sürümünü bilgisayarına kuracak.
en.WelcomeLabel1=Welcome to BÖRÜ
en.WelcomeLabel2=BÖRÜ is a meticulous wolf on your desktop that looks after you and your project while you build games and projects with AI (Claude Code, Codex).%n%nThis wizard will install BÖRÜ {#Surum} on your computer.

[CustomMessages]
tr.Masaustu=Masaüstüne kısayol koy
tr.Baslat=BÖRÜ'yü şimdi başlat (Claude Code / Codex bağlantısını sorar)
tr.BlenderBaslik=Blender bulunamadı
tr.BlenderAlt=Yalnız 3B paketi için gerekir.
tr.BlenderMetin=Bu bilgisayarda Blender (C:\Program Files\Blender Foundation) bulunamadı.%n%nKuruluma devam edebilirsin; canlı kurt, bağlantılar ve çalışma yöntemi Blender olmadan çalışır. Yalnız 3B paketinin adımları için Blender 5 kurman gerekir (blender.org). Başka bir yere kuruluysa BÖRÜ'nün panelinden yolunu gösterebilirsin.
en.Masaustu=Create a desktop shortcut
en.Baslat=Launch BÖRÜ now (it will offer to connect Claude Code / Codex)
en.BlenderBaslik=Blender not found
en.BlenderAlt=Needed for the 3D pack only.
en.BlenderMetin=Blender was not found on this computer (C:\Program Files\Blender Foundation).%n%nYou can continue; the live wolf, connections and the working method work without Blender. Only the 3D pack's steps need Blender 5 (blender.org). If it is installed elsewhere, point BÖRÜ to it from its panel.

[Tasks]
Name: "masaustu"; Description: "{cm:Masaustu}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\{#Exe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#Ad}"; Filename: "{app}\{#Exe}"; Comment: "Yapay zekâyla çalışırken emeğini koruyan kurt"
Name: "{group}\{cm:UninstallProgram,{#Ad}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#Ad}"; Filename: "{app}\{#Exe}"; Tasks: masaustu; Comment: "Yapay zekâyla çalışırken emeğini koruyan kurt"

[Run]
Filename: "{app}\{#Exe}"; Description: "{cm:Baslat}"; Flags: nowait postinstall skipifsilent

[Code]
var
  BlenderSayfasi: TOutputMsgWizardPage;

function BlenderVar: Boolean;
var
  B: TFindRec;
  Kok: String;
begin
  Result := False;
  Kok := ExpandConstant('{commonpf64}') + '\Blender Foundation\';
  if FindFirst(Kok + '*', B) then
  try
    repeat
      if (B.Attributes and FILE_ATTRIBUTE_DIRECTORY <> 0) and FileExists(Kok + B.Name + '\blender.exe') then
      begin
        Result := True;
        Exit;
      end;
    until not FindNext(B);
  finally
    FindClose(B);
  end;
end;

procedure InitializeWizard;
begin
  BlenderSayfasi := CreateOutputMsgPage(wpSelectTasks, CustomMessage('BlenderBaslik'), CustomMessage('BlenderAlt'), CustomMessage('BlenderMetin'));
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := (PageID = BlenderSayfasi.ID) and BlenderVar;
end;
