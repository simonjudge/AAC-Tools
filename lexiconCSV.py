import sys, string, re, os

if len(sys.argv) < 2:
    sys.exit('Usage: %s database-name' % sys.argv[1])
if os.path.isfile(sys.argv[1]): 
    try: 
        s = open(sys.argv[1], 'r').read()
    except IOError as e:
       print 'Oh dear.', sys.argv[1], 'doesn\'t exist'  
    f = open('output.txt', 'w')
    matches = re.findall("[a-zA-Z ']{2,}", s)
    for item in matches:
      f.write("%s\n" % item)
    f.close()
       
