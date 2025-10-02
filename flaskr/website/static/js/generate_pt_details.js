import { Faker, en, en_AU } from 'https://cdn.jsdelivr.net/npm/@faker-js/faker@10.0.0/+esm';

/*
Returns null if field does not exist
Otherwise returns the data in the field
*/
function insertIntoField(name, data) {
    const $field = $(`[name='${name}']`);
    if ($field.length === 0) return;

    const currentVal = $field.val();
    if (currentVal && currentVal.trim() !== "") {
        return currentVal; // already has data
    }

    $field.val(data);
    return data;
}

function randomFutureMonthYear() {
    const now = new Date();
    const future = new Date(
        now.getFullYear() + Math.floor(Math.random() * 5), // 0–4 years ahead
        Math.floor(Math.random() * 12)
    );
    const mm = String(future.getMonth() + 1).padStart(2, "0");
    const yyyy = future.getFullYear();
    return `${mm}/${yyyy}`;
}


function generatePtData() {
    const f = new Faker({ locale: [en_AU, en] });

    // Basic
    let sex = insertIntoField("basic-sex", Math.random() > 0.5 ? "male" : "female");
    let lname = insertIntoField("basic-lastName", f.person.lastName(sex));
    let fname = insertIntoField("basic-givenName", f.person.firstName());

    let titles = ["dr"];
    if (sex === "male") titles.push("mr");
    else if (sex === "female") titles.push("ms", "mrs");
    else titles.push("mr", "ms", "mrs");
    insertIntoField("basic-title", titles[Math.floor(Math.random()*titles.length)]);
    
    insertIntoField("basic-dob", f.date.birthdate({min:1,max:90,mode:"age"}).toISOString().slice(0,10));

    // Basic-Contact
    let state = insertIntoField("basic-state", ["sa","vic","nsw","qld","wa","tas","nt","act"][Math.floor(Math.random()*8)]);
    
    const postcodeRanges = {
        "nsw": [[1000, 1999], [2000, 2599], [2619, 2899], [2921, 2999]],
        "act": [[ 200,  299], [2600, 2618], [2900, 2920]],
        "vic": [[3000, 3996], [8000, 8999]],
        "qld": [[4000, 4999], [9000, 9999]],
        "sa":  [[5000, 5999]],
        "wa":  [[6000, 6999]],
        "tas": [[7000, 7999]],
        "nt":  [[ 800,  999]]
    };
    let range = postcodeRanges[state][Math.floor(Math.random() * postcodeRanges[state].length)];
    let postcode = Math.floor((Math.random() * range[1] - range[0]) + range[0]);
    postcode = String(postcode).padStart(4, "0");

    insertIntoField("basic-postcode", postcode);
    insertIntoField("basic-address", f.location.streetAddress());
    insertIntoField("basic-suburb", f.location.city());

    insertIntoField("basic-phone", "08" + String(Math.floor(Math.random()*99999999)).padStart(8, "0"));
    insertIntoField("basic-mobile", "04" + String(Math.floor(Math.random()*99999999)).padStart(8, "0"));
    insertIntoField("basic-email", f.internet.email({firstName: fname, lastName: lname,}));
    
    // Basic-Medicare
    insertIntoField("basic-medicare", f.number.int({min:100000000,max:999999999}));
    insertIntoField("basic-medicareIssue", f.number.int({min:1,max:9}));
    insertIntoField("basic-medicareSurname", lname);
    insertIntoField("basic-medicareGivenName", fname);
    insertIntoField("basic-medicareValidTo", randomFutureMonthYear());
}

$("#generatePtDetails").on("click", generatePtData);
