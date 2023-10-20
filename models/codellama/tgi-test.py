import requests


HOST = "gr053"
PORT = "8000"

headers = {
    "Content-Type": "application/json",
}

INSTRUCTION_KEY = "[INST]Return a text summary of the following script of code that will be presented to you between [CODE] and [/CODE] tags:[/INST]\n"
PROMPT_KEY = """
[CODE]
void run_void(Render$1 this)

{
  int iVar1;
  int iVar2;
  BufferedImage pBVar3;
  boolean[] pbVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  JFrame pJVar8;
  ImageIcon objectRef;
  BufferedImage pBVar9;
  ImageIcon pIVar10;
  Cursor objectRef_00;
  Render pRVar11;
  JLabel pJVar12;
  JSettings objectRef_01;

  Thread.sleep(500);
  pRVar11 = this.this$0;
  pBVar3 = new(BufferedImage);
  pJVar12 = this.val$iv;
  pBVar9 = pBVar3;
  iVar1 = pJVar12.getWidth();
  pJVar12 = this.val$iv;
  iVar2 = pJVar12.getHeight();
  pBVar3.<init>(iVar1,iVar2,1);
  Render.access$0(pRVar11,pBVar9);
  pJVar12 = this.val$iv;
  objectRef = new(ImageIcon);
  pIVar10 = objectRef;
  pBVar3 = Render.access$1(this.this$0);
  objectRef.<init>(pBVar3);
  pJVar12.setIcon(pIVar10);
  pJVar12 = this.val$iv;
  pJVar12.repaint();
  Render.access$2(this.this$0,false);
  pJVar12 = this.val$iv;
  objectRef_00 = new(Cursor);
  objectRef_00.<init>(0);
  pJVar12.setCursor(objectRef_00);
    objectRef_00 = new(Cursor);
  objectRef_00.<init>(0);
  pJVar12.setCursor(objectRef_00);
  do {
    iVar1 = 0;
    while( true ) {
      iVar2 = iVar1;
      pbVar4 = Render.access$3(this.this$0);
      if (pbVar4.length <= iVar2) break;
      pbVar4 = Render.access$3(this.this$0);
      pbVar4[iVar1] = false;
      iVar1 = iVar1 + 1;
    }
    Render.access$4(this.this$0);
    pJVar12 = this.val$iv;
    pJVar12.repaint();
    pbVar4 = Render.access$3(this.this$0);
    if (pbVar4[0] != false) {
      Render.access$2(this.this$0,true);
      Render.access$5(this.this$0,this.val$f,this.val$iv,this.val$hh);
    }
    pbVar4 = Render.access$3(this.this$0);
    if (pbVar4[1] != false) {
      System.exit(-1);
    }
    pbVar4 = Render.access$3(this.this$0);
    if (pbVar4[2] != false) {
      Render.access$6(this.this$0);
      objectRef_01 = new(JSettings);
      objectRef_01.<init>(0,0,null,0,0,0);
      iVar1 = Render.access$7(this.this$0);
      iVar2 = Render.access$8(this.this$0);
      pJVar8 = this.val$frame;
      iVar7 = 0x20;
      pBVar3 = Render.access$1(this.this$0);
      iVar5 = pBVar3.getWidth();
      pBVar3 = Render.access$1(this.this$0);
      iVar6 = pBVar3.getHeight();
      objectRef_01.main(iVar1,iVar2,pJVar8,iVar7,iVar5,iVar6);
    }
    Thread.sleep(100);
  } while( true );
}
[/CODE]
"""
input_json = INSTRUCTION_KEY + PROMPT_KEY
data = {
    'inputs': input_json,
    'parameters': {
        'max_new_tokens': 2000,
    },
}

response = requests.post(f'http://{HOST}:{PORT}/generate', headers=headers, json=data)
print(response.json())
