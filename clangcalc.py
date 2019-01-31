from subprocess import run
import traceback
from os import remove
 

def calc(answer,stdanswer):
    score=0
    point=0
    print("atd:",stdanswer)
    stdanswer=stdanswer.split("\n\n")
    print("sliped:",stdanswer)
    try:
        with open('stu.c','w',encoding='utf-8') as stuf:
            stuf.write(answer)
    except:
        traceback.print_exc()
        return "ERROR"
    try:
        with open('std.c','w',encoding='utf-8') as stdf:
            stdf.write(stdanswer[0])
    except:
        traceback.print_exc()
        return "ERROR"
    try:i=run('gcc stu.c')
    except:
        traceback.print_exc()
        return 0
    else:
        if i.returncode!=0:
            return 0
    try:i=run('gcc std.c -o b.exe')
    except:
        traceback.print_exc()
        return "ERROR"
    else:
        if i.returncode!=0:
            return "ERROR"
        print(i)
        if len(stdanswer)!=2:
            return "ERROR"
        for each in stdanswer[1].split("|||"):
            print(each)
            try:a=run("a.exe",input=each,capture_output=True,timeout=2,text=True,shell=True)
            except:
                traceback.print_exc()
                return 0
            else:
                try:b=run("b.exe",input=each,capture_output=True,timeout=1,text=True,shell=True)
                except:
                    traceback.print_exc()
                    return "ERROR"
                else:
                    print(a)
                    print(b)
                    if a.returncode==0 and a.stdout==b.stdout:
                        print(a.stderr,"|",b.stderr)
                        score+=1
                point+=1
    print(score,"/",point)
    # try:
    #     with open('stu.c','w',encoding='utf-8') as stuf:
    #         stuf.write("")
    # except:
    #     traceback.print_exc()
    # try:
    #     with open('std.c','w',encoding='utf-8') as stuf:
    #         stuf.write("")
    # except:
    #     traceback.print_exc()
    return score/point

                    

if __name__ == "__main__":
    print(calc('''#include<stdio.h>
int main(){
    int i,j,k;
    printf("enter i=k:");
    scanf("%d",&k);
    for(i=1;i<=k;i++)
    {
        for(j=1;j<=k-i+1;j++)
        {
            printf(" ");
        }
        for(j=1;j<=i;j++)
        {
            printf("%c",64+j);
        }
        for(j-=2;j>=1;j--)
        {
            printf("%c",64+j);
        }
        printf("\\n");
    }
    int *p;
    *p=12
    return 0;
}''','''#include<stdio.h>
int main(){
    int i,j,k;
    printf("enter i=k:");
    scanf("%d",&k);
    for(i=1;i<=k;i++)
    {
        for(j=1;j<=k-i+1;j++)
        {
            printf(" ");
        }
        for(j=1;j<=i;j++)
        {
            printf("%c",64+j);
        }
        for(j-=2;j>=1;j--)
        {
            printf("%c",64+j);
        }
        printf("\\n");
    }
    return 0;
}

2
|||5
|||7
|||12
'''))

