from subprocess import run,PIPE 

_SED = "sed"

def sed(expression,text):
    return run([_SED,"-e",expression],input=text.encode("utf-8"),stdout=PIPE).stdout.decode()

if __name__=="__main__":
    import sys 
    print(sed(sys.argv[1],sys.argv[2]))
