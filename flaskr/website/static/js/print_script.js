$(document).ready(function() {
  $("#script-print").click(print_scripts);
});

const options = {
  filename: 'prescriptions.pdf',
  margin: 10,
  image: { 
    type: 'jpeg',
    quality: 0.98
  },
  html2canvas: { 
    scale: 2,
    logging: false // disable console output
  }, 
  jsPDF: { 
    unit: 'mm',
    format: 'a4',
    orientation: 'portrait'
  },
};

//const blank_prescription = await get_blank_prescription();
async function get_blank_prescription() {
  try {
    // fetch the HTML from the server
    const response = await fetch("/prescription");
    if (!response.ok) throw new Error("Network response was not ok");

    const html = await response.text();

    // create a container for the new content
    const container = document.createElement("div");
    container.innerHTML = html;

    return container;
  } catch (error) {
    console.error("Error fetching content:", error);
  }
}

async function print_scripts() {
  console.log("Print function called");
  const checkedBoxes = $("#asl-table .asl-check input:checked");
  let select_all = checkedBoxes.length === 0;

  
  // Temp parent container to store the prescriptions
  let $container = $('<div></div>');
  const prescription_container = await get_blank_prescription();

  let prescriptionCount = 0;


  // Loop through prescriptions and append them into container
  $("#asl-table tbody tr").each(function(index) {
    const $row = $(this);
    const $checkbox = $row.find(".asl-check input");
    
    
    if (select_all || $checkbox.is(":checked")) {
      console.log(`Processing prescription ${index}`);
      
      let presc = prescription_container.cloneNode(true);
      const rowId = $row.attr("id"); // "asl-0", "asl-1"
      
      presc = insert_prescription_details(presc, rowId);

      let $wrapper = $('<div></div>').append(presc);
      $wrapper.css({'break-after': 'page','margin-top': '10px'});

      $container.append($wrapper[0]);
      prescriptionCount++;
    }
  });
  
  console.log(`Total prescriptions to print: ${prescriptionCount}`);

  console.log(`Total prescriptions to print: ${prescriptionCount}`);

  if (prescriptionCount === 0) {
      alert("No valid prescriptions found to print!");
      return;
  }
  // print the pdf
  html2pdf().set(options).from($container[0]).save();
}


const id_list = [
  "medicare",
  "pharmaceut-ben-entitlement-no",
  "sfty-net-entitlement-cardholder",
  "rpbs-ben-entitlement-cardholder",
  "name",
  "dob",
  "preferred-contact",
  "address-1",
  "address-2",
  "script-date",
  "pbs",
  "rpbs"
]
const drug_info_ids = [ // prepend `asl_data-X-`
  "prescriber-fname",
  "prescriber-lname",
  "prescriber-title",
  "prescriber-address-1",
  "prescriber-address-2",
  "prescriber-id",
  "prescriber-hpii",
  "prescriber-hpio",
  "prescriber-phone",
  "prescriber-fax",
  "DSPID",
  "status",
  "brand-sub-not-prmt",
  "drug-name" ,
  "drug-code" ,
  "dose-instr",
  "dose-qty"  ,
  "dose-rpt"  ,
  "prescribed-date",
  "paperless"
]

function flatten_dict(dict) {
  let new_dict = {};
  
  for (var key in dict) {
    const value = dict[key];
    
    if (Array.isArray(value)) {
      // create index for each element
      value.forEach((item, index) => {
        if (typeof item === "object" && item !== null) {
          const flattened = flatten_dict(item);
          for (var subkey in flattened) {
            new_dict[`${key}-${index}-${subkey}`] = flattened[subkey];
          }
        } else {
          new_dict[`${key}-${index}`] = item;
        }
      });
    } else if (typeof value === "object" && value !== null) {
      const flattened = flatten_dict(value);
      for (var subkey in flattened) {
        new_dict[`${key}-${subkey}`] = flattened[subkey];
      }
    } else {
      new_dict[key] = value;
    }
  }
  
  return new_dict;
}

// Add details of the prescription to the element
// See comment in prescription.html
// data input accessed via `pt_data`: json
function insert_prescription_details(el, drug_id) {
  console.log(`Inserting details for drug_id: ${drug_id}`);
  // Append data
  id_list.forEach(id => {
    const $el = $(el).find(`#${id}`);
    if (pt_data[id] !== undefined) {
      let data_point = pt_data[id];
      if (data_point === true) {
        data_point = 'x';
      } else if (data_point === false){
        return; //continue
      }
      $el.text(data_point);
    }
  });

  // Append ASL specific data
  drug_info_ids.forEach(id => {
    
    const $el = $(el).find(`#${id}`);
    const new_key = `asl_data-${drug_id.slice(-1)}-${id}`;
    if (flatted_pt_data[new_key] !== undefined) {
      let data_point = flatted_pt_data[new_key];
      if (data_point === true) {
        data_point = 'x';
      } else if (data_point === false){
        return; //continue
      }
      $el.text(data_point);
    }
  });

  // Set pt age
  const $el = $(el).find(`#age`);
  $el.text(years_old(pt_data['dob']));
  return el;
}

/* Expected dob in DD/MM/YYYY form */
function years_old(dob) {
  let pt_dob = dob.split("/");
  let newDate = new Date( pt_dob[2], pt_dob[1] - 1, pt_dob[0]);
  let timeDifference = Date.now() - newDate;
  let pt_age = Math.floor(timeDifference / (1000 * 3600 * 24 * 365));
  return pt_age;
}
