/*
Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.

This program is Free Software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
*/
var textContent, testPageHTML, body;

function isUrl(s) {
  var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/
  return regexp.test(s);
}

function cleanForPrince(){
  var temp = $('iframe', parent.document).contents().children().clone();
  $('script', temp).remove();
  $('style, meta:not([name=author])', temp).remove();
  $('head', temp).prepend($('<meta>').attr('http-equiv','content-type').attr('content', 'text/html; charset=utf-8'));
  var images = $('img', temp);
  n = images.length;
  for(var i = 0; i < n; i++){
    var img = images.eq(i);
    var src = img.attr('src').split('?format')[0].split('/');
    var extension = img.attr('type');
    if(extension == undefined)
      extension = "png";
    else
      extension = extension.split('/')[1].split('+')[0];
    img.attr('src',src[src.length - 1] + '.' + extension);
  }
  var text = temp.html();
  var result = "", tagName = "", c = "", chr = "";
  var n = text.length;
  if (text == null) {
    return false;
    }
  var tag = false, tagNameParsing = false;
  for(var i = 0; i < n; i++){
    chr = text[i];
    c = chr.toLowerCase();
    if(c == '<' && tag == false){
      tag = true;
      tagNameParsing = true;
    }
    else if(tag){
      if(c == ' ')
        tagNameParsing = false;
      else if(c == '>'){
        tagNameParsing = false;
        tag = false;
        if(tagName == 'img')
          result += '/';
        tagName = '';
      }
      else if(tagNameParsing){
        if(c == 'i' && tagName == '')
          tagName += c;
        else if(c == 'm' && tagName == 'i')
          tagName += c;
        else if(c == 'g' && tagName == 'im')
          tagName += c;
      }
    }
    result += chr;
  }
  $('textarea[name=field_book_text_content]', parent.document).val('<html>\n' + result + '\n</html>');
  return false;
}

function changeTag(element, tag){
  var tag = $('<' + tag + '>').html(element.html());
  element.after(tag);
  element.remove();
  return tag;
}

function parseList(text){
  return text.replace("[","").replace("]","").replace(/'/g,"").replace(/,/g,", ");
}

function generateTblContent(title, id, className){
  return $('<li>').addClass(className).append($('<a>').attr('href','#' + id).text(title));
}

function generateToCLine(){
  return generateTblContent("Table of Contents", 'toc-h-1', 'frontmatter');
}

function generateFMLine(title, id){
  return generateTblContent(title, 'frontmatter-h-' + id, 'frontmatter');
}

function generateEMLine(title, id){
  return generateTblContent(title, 'endmatter-h-' + id, 'endmatter');
}

function generatePartLine(title, id){
  return generateTblContent(title,'part-h-' + id, 'part');
}

function addLinksToChapters(chapterContainer, id){
  var chapters = chapterContainer.children();
  var n = chapters.length;
  for(var i = 0; i < n; i++){
    var chap = chapters.eq(i);
    chap.addClass('chapter');
    $('a', chap).attr('href', '#chapter-h-' + id + '-' + (i+1));
  }
  return chapterContainer;
}

function addToC(txt){
  // Add to table of Contents
  var ul = $('<ul>').addClass('toc');
  var beginning = true;
  var counter = 1,  partCounter = 1;
  $('body').prepend($('<div>').addClass('toc').attr('id','toc-h-1').append(ul));
  ul.html(txt);
  ul.append(generateToCLine());
  var headers = $('h1', ul);
  var n = headers.length;
  for(var i = 0; i < n; i++){
    var hdr = headers.eq(i);
    var j = hdr.index() + 1;
    var chapterList = ul.children().eq(j)[0];
    if(chapterList == undefined || chapterList.tagName.toUpperCase() == "UL"){
      beginning = false;
      ul.append(generatePartLine(hdr.text(), partCounter).append(addLinksToChapters($(chapterList), partCounter)));
      partCounter++;
      counter = 1;
    }
    else{
      if(beginning)
        ul.append(generateFMLine(hdr.text(), counter));
      else
        ul.append(generateEMLine(hdr.text(), counter));
      counter++;
    }
  }
  $('> h1', ul).remove();
}

function fetchTextInfo(hasToC, txt){
  $.get('TestPage_getDetail', function(details, status, xhr){
    details = details.split('\n');
    var title = details[0], shortTitle = details[1], description = details[2], authors = parseList(details[3]);
    var year = details[4].split('/')[0];
    var titleObj = $('title');
    if(titleObj.length > 0)
      titleObj.text(title);
    else
      $('head').append($('<title>').text(title));
    $('head').prepend($('<meta>').attr('name','author').attr('content', authors));
    titleObj = $('<h1>').text(title);
    var subtitle = $('<h2>').text(description);
    var edition = $('<h3>').text(shortTitle);

    //Add Table of Contents
    if(hasToC)
      addToC(txt);
    //Add imprint
    $('body').prepend($('<div>').addClass('imprint').append($('<p>').text("Copyright \u00A9 " + year + ' ' + authors)));
    //Add Title Page
    $('body').prepend($('<div>').addClass('titlepage').append(titleObj.clone().addClass('no-toc')).append(subtitle.clone().addClass('no-toc')).append(edition.clone().addClass('no-toc')).append($('<p>').addClass('no-toc').text(authors)));
    //Add Front Cover
    $('body').prepend($('<div>').addClass('frontcover').append($('<img>').attr('src','canvas?format=')).append(titleObj).append(subtitle).append(edition));
    if(hasToC)
      cleanForPrince();
  });
}

function convertChapter(link, container, first, isChapter, chapterCounter, partCounter){
  $(function() {
    //Getting the html content
    $.get(link, function(data, textStatus, jqXHR){
      var chapterContainer = $('<div>').addClass('chapter').attr('id', 'chapter-h-' + partCounter + '-' + chapterCounter).html(data);
      link = link.replace("index_html?format=html","");
      $('test', chapterContainer).remove();
      var sections = $('section', chapterContainer);
      $('base,meta,link,title', chapterContainer).remove();
      changeTag($('footer', chapterContainer), 'p');
      var n = sections.length;
      for(var i = 0; i < n; i++){
        element = changeTag(sections.eq(i), 'div');
        var images = $('> img, details > img', element);
        var otherImages = $('img:not(> img, details > img)', element);
        var p = images.length;
        for(var j = 0; j < p; j++){
          var img = images[j];
          var div = $('<div>');
          var caption = $('<p>').addClass('caption');
          if(isUrl($(img).attr('src')) == false) {
           $(img).attr('src', link + $(img).attr('src'));
          }
          $(img).before(div);
          var imgToAppend = $(img);
          var imgWidth = $(img).attr('width');
          if( imgWidth == undefined || imgWidth == '')
            imgToAppend.attr('width','90%');
          div.addClass('figure').append(caption).append($('<p>').addClass('art').append(imgToAppend));
          caption.text($(img).attr('title'));
        }
        var p = otherImages.length;
        for(var j = 0; j < p; j++){
          var img = otherImages[j];
          if((/^http/).test($(img).attr('src')) == false) {
           $(img).attr('src', link + $(img).attr('src'));
          }
        }
        if(first && i == 0)
          element.attr('style','counter-reset: page 1;');
        else if(i != 0){
          var headers = $(':header', element);
          var j = 0, p = headers.length;
          for(j = 0; j < p; j++){
            var hdr = headers[j];
            changeTag($(hdr), 'H' + (parseInt(hdr.tagName.split('H')[1]) + 1));
          }
        }
        var details = $('details', element);
        details.before(details.html());
        details.remove();
        element.addClass('section');
      }
      //Why using this instead of load? because using load causes errors when the images are loaded, and the process won't reach the end in certain cases
      //Moreover, since we load also descriptions, it's better to do it this way so that the user doesn't see the trick
      chapterContainer.append($('div.section', chapterContainer));
      
      $('test', chapterContainer).remove();
      //If it's a chapter and not the introduction or an appendix for instance
      if(isChapter){
        container.append(chapterContainer);
        cleanForPrince();
      }
      else
        container.append(chapterContainer.children());
      if(container[0].tagName.toUpperCase() == 'BODY'){
        fetchTextInfo(false, '');
      }
    });
  });
}

function convertBook(linkToBook, container){
  $(function() {
    //Getting the html content
    $.get(linkToBook, function(data, textStatus, jqXHR){
      linkToBook = linkToBook.replace('index_html?format=html','');
      var tocContainer = $('<div>').html(data);
      var sections = tocContainer.children();
      body = $('<body>');
      var firstSection = true, firstChapter = true;
      var n = sections.length;
      var partCounter = 0, matterCounter = 1;
      var partContainer = $('<div>');
      for(var i = 0; i < n; i++){
        var section = sections.eq(i);
        var isPart = section[0].tagName.toUpperCase() == 'UL';
        //If it's a list tag, it's a part (containing several chapters)
        if(isPart){
          var chapterTitles = $('> li', section);
          var p = chapterTitles.length;
          for(var j = 0; j < p; j++){
            var newChapter = $('<div>').addClass('chapter').attr('id','chapter-h-' + partCounter + '-' + (j+1));
            partContainer.append(newChapter);
            convertChapter($('> a', chapterTitles.eq(j)).attr('href') + '/index_html?format=html', newChapter, false, false);
          }
          body.append(partContainer);
          firstChapter = false;
          matterCounter = 1;
        }
        else{
          var link = $('> a', section);
          //If there is a link, then it's a frontmatter (or endmatter) like an introduction else it's the title of a part
          if(link.length == 1){
            var newMatter = $('<div>');
            if(firstChapter){
              newMatter.addClass('frontmatter').attr("id","frontmatter-h-" + matterCounter);
              if(firstSection)
                newMatter.attr('style','counter-reset: page 1;');
            }
            else
              newMatter.addClass('endmatter').attr("id","endmatter-h-" + matterCounter);
            body.append(newMatter);
            matterCounter++;
            convertChapter(link.attr('href') + '/index_html?format=html', newMatter, false, false);
          }
          else{
            partCounter++;
            partContainer = $('<div>').addClass('part').attr('id','part-h-' + partCounter).append(section.clone());
          }
        firstSection = false;
        }
      }
      $('body').append(body.children());
      fetchTextInfo(true, data);
    });
  });
}
