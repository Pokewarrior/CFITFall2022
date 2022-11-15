console.log(mode([1.5,2.5,2.5,2.5,1,1]));
function mode(array) {
	const count = {};
	array.forEach(elem => {
	if (!count[elem])  count[elem] = 0
		count[elem]+= 1;
	});
	console.log(count)
	let result = []
	let max = 0;
	for(let key in count){
		if(count[key] > max){result = [key]
			max = count[key]}
		else if (count[key] === max){
			result.push(key)
		}

	} 
	if (Object.keys(count).length === result.length){
		result = "no mode";
		return result
	}
	return result
}

