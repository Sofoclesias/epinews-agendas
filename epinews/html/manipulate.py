
import re
from lxml.html import HtmlElement
import string
import lxml







DIV_TO_P = (
    r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)"
)

CONTAINS_ARTICLE = (
    './/article|.//*[@id="article"]|.//*[contains(@itemprop,"articleBody")]'
)

TAGS_STRINGS = [
    {'tag':'em'},
    {'tag':'img'},
    {'tag':'figure'},
    {'tag':'figcaption'},
    {'tag':'script'},
    {'tag':'style'},
    {'attribs':{'itemprop':'caption'}},
    {'attribs':{'class':'instagram-media'}},
    {'attribs':{"class": "image-caption"}},
    {'attribs':{"class": "caption"},'match':'substring'},
    {'tag':'span','attribs':{"class": "dropcap"},'match':'word'},
    {'tag':'span','attribs':{"class": "drop_cap"},'match':'word'}
]

SOCIAL_MEDIA = [
    "^caption$",
    " google ",
    "^[^entry-]more.*$",
    "[^-]facebook",
    "facebook-broadcasting",
    "[^-]twitter|twitter-tweet",
    r"related[-\s\_]?(search|topics|media|info|tags|article|content|links)|"
    r"(search|topics|media|info|tags|article|content|links)[-\s\_]?related"
]

BAD_ATTRIBS = (
    "^side$|combx|retweet|mediaarticlerelated|menucontainer|"
    "navbar|storytopbar-bucket|utility-bar|inline-share-tools"
    "|comment|PopularQuestions|contact|foot|footer|Footer|footnote"
    "|cnn_strycaptiontxt|cnn_html_slideshow|cnn_strylftcntnt"
    "|links|meta$|shoutbox|sponsor|aside|nav|noscript|menu"
    "|tags|socialnetworking|socialNetworking|cnnStryHghLght"
    "|cnn_stryspcvbx|^inset$|pagetools|post-attributes"
    "|welcome_form|contentTools2|the_answers"
    "|communitypromo|runaroundLeft|subscribe|vcard|articleheadings"
    "|date|^print$|popup|author-dropdown|tools|socialtools|byline"
    "|konafilter|KonaFilter|breadcrumbs|^fn$|wp-caption-text"
    "|legende|ajoutVideo|timestamp|js_replies" 
)

BAD_TAGS = ["aside","nav","noscript","menu"]










def clear_whitespace(text: str):
    return re.sub(r"\t|\r|\f|\v|\n","",text)

def get_tags(
    node: lxml.html.Element,
    tag: str | None = None,
    attribs: dict[str,str] | None = None,
    match: str = 'exact'
):
    if not attribs:
        return node.xpath(f".//{(tag or '*')}")
    
    sels = []
    for k, v in attribs.items():
        trans = 'translate(@%s, "%s","%s")' % (k, string.ascii_uppercase,string.ascii_lowercase)
        
        if match=='exact':
            sels.append('%s="%s"' % (trans, v.lower()))
        elif match=='substring':
            sels.append('contains(%s, "%s")' % (trans, v.lower()))
        elif match =='word':
            sels.append('contains(concat(" ", normalize-space(%s), " "), " %s ")' % (trans,v.lower()))
        
    selector = ".//%s[%s]" % (tag or "*"," and ".join(sels))
    return node.xpath(selector)

def get_tags_regex(
    node: lxml.html.Element,
    tag: str | None = None,
    attribs: dict[str,str] | None = None
):
    namespace = {"re": "http://exslt.org/regular-expressions"}
    sels = []
    for k, v in attribs.items():
        sels.append(f"re:test(@{k}, '{v}', 'i')")
        
    selector = ".//%s[%s]" % (tag or "*", " and ".join(sels))
    return node.xpath(selector,namespaces=namespace)
    
def kill_tags(nodes: HtmlElement | list[HtmlElement]):
    if not isinstance(nodes,list):
        nodes = []
    for node in nodes:
        node.clear()
        node.drop_tag()
    
def drop_tags(nodes: HtmlElement | list[HtmlElement]):
    if not isinstance(nodes,list):
        nodes = []
    for node in nodes:
        node.drop_tag()
        
def clear_tag(doc: HtmlElement, tag: str, attribs: list[str]):
    elements = get_tags(doc,tag=tag)
    
    if elements:
        for attr in attribs:
            elements.attrib.pop(attr, None)
    return doc


# Función integradora
def vacuum(doc: lxml.html.HtmlElement):
    doc = clear_tag(doc,'body',['class'])
    doc = clear_tag(doc,'article',['id','name','class'])
    
    bad_tags = [get_tags(doc, tag=tagx) for tagx in BAD_TAGS]
    bad_tags += get_tags_regex(doc,attribs={'id':BAD_ATTRIBS})
    bad_tags += get_tags_regex(doc,attribs={'class':BAD_ATTRIBS})
    bad_tags += get_tags_regex(doc,attribs={'name':BAD_ATTRIBS})
    
    for conditions in TAGS_STRINGS:
        bad_tags += get_tags(doc,**conditions)    
    
    for expression in SOCIAL_MEDIA:
        bad_tags += get_tags_regex(doc,attribs={'id':expression})
        bad_tags += get_tags_regex(doc,attribs={'class':expression})
    
    for node in bad_tags:
        kill_tags(node)
        
    drop_tags(doc.xpath(".//p/span"))
    
    for item in get_tags(doc, tag="body")[0].iter():
        if item.tag not in ['p','br','h1','h2','h3','h4','h5','h6','ul','body','article','section']:
            if item.text is None and item.tail is None:
                item.drop_tag()
                
    return doc