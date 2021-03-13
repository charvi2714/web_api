function myFunction(a, b) {
    console.log(a * b);
    document.getElementById('test').innerHTML = String(a * b);
    console.log('hi');
}
//
// window.onload = (event) => {
//   console.log('page is fully loaded');
//   postData();
// };
//
// async function postData() {
//     // Default options are marked with *
//     const response = await fetch('http://127.0.0.1:5000/somanytesting');
//     console.log(response);
// }