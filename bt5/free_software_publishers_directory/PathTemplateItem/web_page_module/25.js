//////////////////////////////////////////////////
// Parse Data to Get Data Sheets for Publeshers
// and for Softwares.
// They have a portal_type property to differenciate
// them from each other.
// portal_type values belong to :
//   ["publisher", "software"]
//////////////////////////////////////////////////
function createAllDataSheets () {
  return publisher_storage.allDocs()
  .push(function (data) {
    var publisher_id_list = [];

    for (var i in data.data.rows) {
      var id = data.data.rows[i].id;
      if(id.indexOf("_replicate_") < 0) {
        publisher_id_list.push(id);
      }
    }

    var promise_list = [];

    function setPortalTypeOnPublisher (j) {
      return publisher_storage.get(publisher_id_list[j])
      .push(function (publisher_object) {
        publisher_object.portal_type = "publisher";
        return publisher_storage.put(publisher_id_list[j], publisher_object);
      });
    };

    for(var i in publisher_id_list) {
      promise_list.push(setPortalTypeOnPublisher(i));
    }

    return RSVP.all(promise_list);
  })

  // Create all the software Documents
  .push(function () {
    return publisher_storage.allDocs({
      select_list: ['title', 'free_software_list'],
      query: 'portal_type: "publisher"'
    });
  })
  .push(function (publisher_list) {
    var promise_list = [];
    
    function saveSoftwareDocument (publisher, software) {
      software.portal_type = "software";
      software.publisher = publisher;
      return publisher_storage.put(software.title, software)
    }

    function saveSoftwareListFromPublisher (j) {
      var publisher = publisher_list.data.rows[j].value.title,
        software_list = publisher_list.data.rows[j].value.free_software_list;
      
      var save_software_promise_list = []
      
      for (var i in software_list) {
        save_software_promise_list.push(saveSoftwareDocument(publisher, software_list[i]))
      }

      return RSVP.all(save_software_promise_list);
    }
    
    for (var i in publisher_list.data.rows) {
      promise_list.push(saveSoftwareListFromPublisher(i));
    }
    
    return RSVP.all(promise_list);
  });
}

//////////////////////////////////////////////////
// Displays the Publisher list in the DOM
//////////////////////////////////////////////////
function displayPublisherList(publisher_list) {
  var publisher_list_element = document.querySelector('.publisher_list');

  for(var i in publisher_list.rows) {
    var publisher = publisher_list.rows[i].value;
    
    var template = document.querySelector("#publisher_list_item"),
      template_logo = template.content.querySelector(".logo img"),
      template_title = template.content.querySelector(".title"),
      template_country = template.content.querySelector(".country"),
      template_website = template.content.querySelector(".website a"),
      template_founded_year = template.content.querySelector(".founded_year"),
      template_presence_list = template.content.querySelector(".presence_list");
    
    template_title.textContent = publisher.title;
    template_logo.setAttribute("src", publisher.logo);
    template_country.textContent = publisher.country;
    template_website.textContent = publisher.website;
    template_website.setAttribute("href", publisher.website);
    template_founded_year.textContent = publisher.founded_year;
    
    var list_item_string = "";

    for(var i in publisher.presence) {
       list_item_string += "<li>" + publisher.presence[i] + "</li>";
      template_presence_list.innerHTML = list_item_string;
    }
    
    var content = document.importNode(template.content, true);
    publisher_list_element.appendChild(content);
  }
};

//////////////////////////////////////////////////
// Displays the Software list in the DOM
//////////////////////////////////////////////////
function displaySoftwareList(software_list) {
  var software_list_element = document.querySelector('.software_list');

  for (var i in software_list.rows) {
    var software = software_list.rows[i].value;
    
    var template = document.querySelector("#software_list_item"),
      template_logo = template.content.querySelector(".logo img"),
      template_title = template.content.querySelector(".title"),
      template_publisher = template.content.querySelector(".publisher"),
      template_category_list = template.content.querySelector(".category_list"),
      template_source_code_download = template.content.querySelector(".source_code_download a"),
      template_commercial_support = template.content.querySelector(".commercial_support a"),
      template_wikipedia_url = template.content.querySelector(".wikipedia_url a");
      
    template_title.textContent = software.title;
    template_publisher.textContent = software.publisher;
    template_logo.setAttribute("src", software.logo)
    template_source_code_download.textContent = software.source_code_download;
    template_source_code_download.setAttribute("href", software.source_code_download);
    template_commercial_support.textContent = software.commercial_support;
    template_commercial_support.setAttribute("href", software.commercial_support);
    template_wikipedia_url.textContent = software.wikipedia_url;
    template_wikipedia_url.setAttribute("href", software.wikipedia_url);

    var list_item_string = "";
    for(var i in software.category_list) {
      var category = software.category_list[i];
      list_item_string += "<li>" + category + "</li>";
      template_category_list.innerHTML = list_item_string;

      if (software_category_list.indexOf(category) < 0) {
        software_category_list.push(category);
      }
    }

    var content = document.importNode(template.content, true);
    software_list_element.appendChild(content);
  }
};

//////////////////////////////////////////////////
// Displays the Software category list select field
//////////////////////////////////////////////////
function displaySoftwareCategorySelectField() {
  var select_field = document.querySelector(".category_list_select_field");

  software_category_list.sort();

  for (var i in software_category_list) {
    var category = software_category_list[i];
    select_field.innerHTML += "<option value=\"" +
                              category + "\">" +
                              category + "</option>";
  }
};

//////////////////////////////////////////////////
// MAIN FUNCTION
//////////////////////////////////////////////////
window.onload = function () {
  publisher_storage.repair()
  .push(function () {
    return createAllDataSheets();
  })
  .push(function (data) {
    return publisher_storage.allDocs({
      select_list: ['title', 'logo', 'country', 'presence', 'website', 'founded_year', 'free_software_list'],
      query: 'portal_type: "publisher"',
    });
  })
  .push(function (data) {
    displayPublisherList(data.data);
    return publisher_storage.allDocs({
      select_list: ['title', 'logo', 'category_list', 'source_code_download', 'commercial_support', 'wikipedia_url', 'success_case_list', 'publisher'],
      query: 'portal_type: "software"',
    })
  })
  .push(function (data) {
    displaySoftwareList(data.data);
    displaySoftwareCategorySelectField();
  })
  .push(undefined, function (error) {
    console.log(error);
  });
};