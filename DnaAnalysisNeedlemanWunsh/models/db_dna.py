import math, random, uuid, re

db.define_table('dna',
   Field('name'),
   Field('sequence','text'))

def random_gene(n):
   return ''.join(['ATGC'[int(n+10*math.sin(n*k)) % 4] for k in range(10+n)])+'UAA'

def random_dna():
   return ''.join([random_gene(random.randint(0,10)) for k in range(50)])

# if not data make some up
if not db(db.dna.id>0).count():   
   for k in range(100):
      db.dna.insert(name=uuid.uuid4(), sequence=random_dna())
       
def find_gene_size(a):
   """locates genes in sequence and compute their lengths"""
   r=re.compile('(UAA|UAG|UGA)(?P<gene>.*?)(UAA|UAG|UGA)')
   return [(g.start(),len(g.group('gene'))) for g in r.finditer(a)]

def needleman_wunsch(a,b,p=0.97):
   """Needleman-Wunsch and Smith-Waterman"""   
   z=[]
   for i,r in enumerate(a):
       z.append([])
       for j,c in enumerate(b):
           if r==c: z[-1].append(z[i-1][j-1]+1 if i*j>0 else 1)
           else: z[-1].append(p*max(z[i-1][j] if i>0 else 0,z[i][j-1] if j>0 else 0))  
   return z
