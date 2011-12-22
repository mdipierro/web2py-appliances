db.rdf_namespaces = {'_xmlns:rdf':"http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
                     '_xmlns:relational':"http://www.dbs.cs.uni-duesseldorf.de/RDF/relational.owl#"
                    }

db.define_table('post', 
                Field('author', 'string'),
                Field('title', 'string'),
                Field('body', 'text'))

#db.post.author.rdf = 'sioc:has_creator'
db.post.title.rdf = 'dc:title'
db.post.body.rdf = 'sioc:content'
db.post.author.rdf = { 'name':'sioc:has_creator',
                       'children': [ { 'name':'sioc:User',
                                       '_rdf:about':'http://chrisbaron.com',
                                       '_rdf:label':'$VALUE',
                                       'children': [ { 'name':'rdf:seeAlso',
                                                       '_rdf:resource':'http://web2py.com'
                                                   } ]
                                   } ]
                     }  


db.post.rdf = {
    'type': 'http://rdfs.org/sioc/ns#Post',
    'references': { 'comment': 'sioc:has_reply' },
    'namespaces': {
                     "_xmlns:dc":"http://purl.org/dc/elements/1.1/",
                     "_xmlns:sioc":"http://rdfs.org/sioc/ns#"
                  }
              }

db.define_table('comment',
                Field('post_id', db.post),
                Field('author', 'string'),
                Field('body', 'text'))

db.comment.author.rdf = 'sioc:has_creator'
db.comment.body.rdf = 'sioc:content'

db.comment.rdf = { 
    'type': 'http://rdfs.org/sioc/ns#Post',
    'namespaces': { "_xmlns:sioc":"http://rdfs.org/sioc/ns#" }
}
    
db.define_table('tag',
                Field('name', 'string'))

db.tag.name.rdf = 'sioc:content'

db.tag.rdf = { 
    'type': 'http://rdfs.org/sioc/ns#topic',
    'namespaces': { "_xmlns:sioc":"http://rdfs.org/sioc/ns#" }
}

db.define_table('post_tag_link',
                Field('post_id', db.post),
                Field('tag_id', db.tag),
                Field('ranking', 'integer'))

db.post_tag_link.rdf_mapping = { 'post': { 'reference': 'sioc:topic',
                                           'columns': { 'ranking': 'sioc:tagRank' } } }

if not db(db.post.id>0).count():
    post_id_1 = db.post.insert(author = "Chris Baron",
                             title = "How To Publish RDF Using web2py",
                             body = "How To Publish RDF Using web2py, really")

    post_id_2 = db.post.insert(author = "Massimo Di Pierro",
                             title = "How To Create a Web Application",
                             body = "Use web2py.")
    
    db.comment.insert(post_id = post_id_1,
                      author = "Jon Doe",
                      body = "I like your post")

    db.comment.insert(post_id = post_id_2,
                      author = "Jane Doe",
                      body = "I don't like your post")

    tag_id_1 = db.tag.insert(name = "RDF")
    tag_id_2 = db.tag.insert(name = "web2py")
    
    db.post_tag_link.insert(post_id = post_id_1,
                            tag_id = tag_id_1,
                            ranking = 10)
    
    db.post_tag_link.insert(post_id = post_id_2,
                            tag_id = tag_id_2,
                            ranking = 5)

