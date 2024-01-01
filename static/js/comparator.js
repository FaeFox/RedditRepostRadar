
/**
 * Shows a toastr message using the SweeetAlert2 methods.
 * @param {string} message - Message to show.
 * @param {string} type - Type of the toastr( 'success', 'error', 'warning', 'info').
 * @param {number} duration - Duration in ms
 */
function showToast(type = "success",  message, duration = 3000){
    const Toast = Swal.mixin({
       toast: true,
       position: "top-end",
       showConfirmButton: false,
       timer: duration,
       timerProgressBar: true,
          didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
           }
      });

    Toast.fire({
      icon: type,
      title:message
    });


}



function validateForm() {
 var outputDirName = document.getElementById("output_dir_name").value;
 var startDate = document.getElementById("start_date").value;
 var subredditName = document.getElementById("subreddit_name").value;
 var imageLimit = document.getElementById("image_limit").value;
 var baseFolder = document.getElementById("base_folder").value;
 //var generateJsonReport = document.getElementById("generate_json_report").checked;
 var writeToMongoDB = document.getElementById("write_to_mongodb").checked;

 if (!outputDirName || !startDate || !subredditName || !imageLimit || !baseFolder) {
    showToast("error", "Please fill in all required fields before starting the scraper.");
    return false;
}
  
 //MongoDB things
 if (writeToMongoDB && (!document.getElementById("mongo_connection_string").value || !document.getElementById("mongo_database").value || !document.getElementById("mongo_collection").value)) {
   showToast("error", "Please fill in all required fields before starting the scraper.");
   return false;
 }

 return true;
}


//Shows or unshows the mongo settings
function toggleMongoSettings() {
   var checkBox = document.getElementById("write_to_mongodb");
   var mongoSettings = document.getElementById("mongo_settings");
   mongoSettings.style.display = checkBox.checked ? "block" : "none";
}


// Function that checks if dark mode is enabled
function isDarkMode() {
   // Get the current value of data-bs-theme attribute on the root HTML element
   const currentTheme = document.documentElement.getAttribute('data-bs-theme');
   
   // Check if the current theme is 'dark'
   return currentTheme === 'dark';
}

//Function that toggles the dark mode using the button
function toggleDarkMode() {
// Get the dark toggle checkbox
   const checkbox = document.getElementById('checkbox');

   // if it's checked then set the dark theme
   if (checkbox.checked) {
   document.documentElement.setAttribute('data-bs-theme', 'dark');
   } else {
   // otherwise go with the white theme
    document.documentElement.removeAttribute('data-bs-theme');
   }

}

//Checks scraper progress
function checkProgress() {
   fetch('/scrape_progress')
       .then(response => response.json())
       .then(data => {
           var progressBar = document.getElementById("progressBar");
           progressBar.style.width = data.progress + '%';
           progressBar.innerText = data.progress + '%';

           if (data.progress < 100) {
               setTimeout(checkProgress, 1000); // Poll every second
           }
       });
}


document.addEventListener('DOMContentLoaded', function() {
   console.log("toggleMongoSettings")
   toggleMongoSettings();

}, false);



document.addEventListener('DOMContentLoaded', function() {
    console.log("toggleMongoSettings")
    toggleMongoSettings();
    //setupSocket();
}, false);

      // Funzione per aggiornare la barra di avanzamento
      function updateProgressBar(progress) {
        var progressBar = document.getElementById('progressBar');
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.innerText = progress + '%';
    }


    function downloadImages(){
        var socket = io().connect('http://' + document.domain + ':' + location.port);

       //Triggers the start_scraper event
       socket.emit('start_scraper');
        
        //whenever the update_scraper_progress event is sent from the backend... log the progress (data is the JSON received from the BE)
        socket.on('update_scraper_progress', function(data) {
            console.log('Progress:', data.progress);
            updateProgressBar(data.progress);
        });
        
        //same as above, when the status is completed then we send the message download complete.
        socket.on('download_complete', function() {
            console.log('Download complete!');
        });
    }


function startScraper() {
   if (validateForm()) {
       // Something?
       showToast("success", "Scraper started!");
       downloadImages();
       
   }
}



/**
 * Shows a toastr message using the SweeetAlert2 methods.
 * @param {string} message - Message to show.
 * @param {string} type - Type of the toastr( 'success', 'error', 'warning', 'info').
 * @param {number} duration - Duration in ms
 */
function showToast(type = "success",  message, duration = 3000){
    const Toast = Swal.mixin({
       toast: true,
       position: "top-end",
       showConfirmButton: false,
       timer: duration,
       timerProgressBar: true,
          didOpen: (toast) => {
              toast.onmouseenter = Swal.stopTimer;
              toast.onmouseleave = Swal.resumeTimer;
           }
      });

    Toast.fire({
      icon: type,
      title:message
    });


}




function validateForm() {
    var baseFolder = document.getElementById("base_folder").value;
    var imageLimit = document.getElementById("image_limit").value;
    var writeToMongoDB = document.getElementById("write_to_mongodb").checked;

    if (!baseFolder || !imageLimit) {
        showToast( "error", "Please fill in all the required fields.");
        return false;
    }

    if (writeToMongoDB && (!document.getElementById("mongo_connection_string").value || !document.getElementById("mongo_database").value || !document.getElementById("mongo_collection").value)) {
        showToast( "error", "Please fill in all MongoDB settings when MongoDB integration is enabled.");
        return false;
    }

    return true;
}



//Shows or unshows the mongo settings
function toggleMongoSettings() {
   var checkBox = document.getElementById("write_to_mongodb");
   var mongoSettings = document.getElementById("mongo_settings");
   mongoSettings.style.display = checkBox.checked ? "block" : "none";
}


// Function that checks if dark mode is enabled
function isDarkMode() {
   // Get the current value of data-bs-theme attribute on the root HTML element
   const currentTheme = document.documentElement.getAttribute('data-bs-theme');
   
   // Check if the current theme is 'dark'
   return currentTheme === 'dark';
}

//Function that toggles the dark mode using the button
function toggleDarkMode() {
// Get the dark toggle checkbox
   const checkbox = document.getElementById('checkbox');

   // if it's checked then set the dark theme
   if (checkbox.checked) {
   document.documentElement.setAttribute('data-bs-theme', 'dark');
   } else {
   // otherwise go with the white theme
    document.documentElement.removeAttribute('data-bs-theme');
   }

}

//Checks scraper progress
function checkProgress() {
   fetch('/scrape_progress')
       .then(response => response.json())
       .then(data => {
           var progressBar = document.getElementById("progressBar");
           progressBar.style.width = data.progress + '%';
           progressBar.innerText = data.progress + '%';

           if (data.progress < 100) {
               setTimeout(checkProgress, 1000); // Poll every second
           }
       });
}


function initializeDropzone(){
    Dropzone.options.comparatorDropzone = { // camelized version of the `id`
        paramName: "file", // The name that will be used to transfer the file
        maxFilesize: 2, // MB
        accept: function(file, done) {
          if (file.name == "justinbieber.jpg") {
            done("Naha, you don't.");
          }
          else { done(); }
        }
      };
}


document.addEventListener('DOMContentLoaded', function() {
   console.log("toggleMongoSettings")
   toggleMongoSettings();
   initializeDropzone();
}, false);

function startScraper() {
   if (validateForm()) {
       // Something?
       showToast("success", "Scraper started!");
   }
}


