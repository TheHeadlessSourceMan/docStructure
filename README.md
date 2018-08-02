# docStructure
![Status: Stable](https://img.shields.io/badge/status-stable-green.svg?style=plastic)
![Python Version: 2.7](https://img.shields.io/badge/Python%20Version-2.7-blue.svg?style=plastic)
![Release Version: 1.0](https://img.shields.io/badge/Release%20Version-1.0-green.svg?style=plastic)
[![webpage:click here](https://img.shields.io/badge/webpage-click%20here-blue.svg?style=plastic)](https://theheadlesssourceman.wordpress.com/2018/08/02/docstructure/)

License - LGPL

Allows simple, sophisticated access to word processor text documents.

* Plug-in based support for unlimited file formats.
* You can get simple string access to a document regardless of whether it’s marked up or not. e.g. myDoc[5]=’x’
* You can find document elements. myDoc.chapter[1].word[19]
* You can find document elements in a flat manner. ‘the’==myDoc.word[19] or myDoc.sentence[5]
* Get linguistic info on elements. myDoc.word[19].partOfSpeech or myDoc.word[19].definition
* All documents can be reduced to plain text or html for universal display/conversion. myDoc.text or myDoc.html

Uses:

* Grammar/spelling checker. (for instance, “grammarcheck“)
* Document viewer (possibly web-based).
* Document type conversion.
* Data mining.
* Grep searching.
* Natural language processing.
* Machine learning.

	
Examples:

Can load complex file formats and get useful info.

    d=Document('myDoc.odf')
    > d.author
    William Shakespere


It’s easy to get important stats.

    > d.numWords
    105

    > d.numChapters
    2

The document can be accessed flatly, or in a hierarchy.

    > d.chapter[0].word[0]
    The
    > d.chapter[0].word[1]
    I
    > d.word[0]
    The

It can attempt to deduce who a pronoun is referencing.

    > d.word[7]
    he
    > d.word[7].partOfSpeech
    pronoun
    > d.word[7].refersTo
    Fred

	
You can always access the document as simple string (a useful trick for marked up documents!)

    > d.find('Fred')
    27
    > d[27]
    F
    > d[27:3]
    Fre

Get any document as plain text or html

    > d.html='This is a document.'
    > d.text
    This is a document

 
Combine concepts.

    > d.word[7][0:4]
    Fred
    > d.chapter[5].html='This is a document.'


Notes:

* When passing into other code to use as string, beware of “if type(x)==str:” In this case, your code will NOT treat a Document as a str!
* also beware of file.write(doc) this would write a flattened string, which may or may not be what you want. Alternatives: doc.save(filename) or file.write(doc.html)

Status:

* Has a basic implementation that more or less works.
* Currently working under the assumption of flatten=>use=>replace_selection where each document fragment contains an index into the document for quick finding
* This length counting makes indexing fast, but replacements early in the file slow.

TODO:

* Insert+index could be speeded up using offset from parent element. It slows down read index, but could be a good compromise.
* Inserting across elements is an unknown. e.g. replace “bears love” in “happy bears love”
* Still need to develop a concept for single character representation, such as html ”<br/>” = “\n” and “>” = “>”

Links:

Main webpage:
https://theheadlesssourceman.wordpress.com/2018/08/02/docstructure/