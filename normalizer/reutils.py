import re

general_nodes = (
    "^side$|combx|retweet|mediaarticlerelated|menucontainer|"
    "navbar|storytopbar-bucket|utility-bar|inline-share-tools"
    "|comment|PopularQuestions|contact|foot|footer|Footer|footnote"
    "|cnn_strycaptiontxt|cnn_html_slideshow|cnn_strylftcntnt"
    "|links|meta$|shoutbox|sponsor"
    "|tags|socialnetworking|socialNetworking|cnnStryHghLght"
    "|cnn_stryspcvbx|^inset$|pagetools|post-attributes"
    "|welcome_form|contentTools2|the_answers"
    "|communitypromo|runaroundLeft|subscribe|vcard|articleheadings"
    "|date|^print$|popup|author-dropdown|tools|socialtools|byline"
    "|konafilter|KonaFilter|breadcrumbs|^fn$|wp-caption-text"
    "|legende|ajoutVideo|timestamp|js_replies"      
)

related_nodes = (
    r"related[-\s\_]?(search|topics|media|info|tags|article|content|links)|"
    r"(search|topics|media|info|tags|article|content|links)[-\s\_]?related"
)

div_to_p = (
    r"<(a|blockquote|dl|div|img|ol|p|pre|table|ul)"
)

contains_article = (
    './/article|.//*[@id="article"]|.//*[contains(@itemprop,"articleBody")]'
)