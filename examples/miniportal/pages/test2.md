title: Test 2

# array #

Array utilities.


## append(arr1, arr2):Array

Appends an array to the end of the other.
The first array will be modified and will contain the appended items.

See: [`union()`](#union), [`combine()`](#combine)

```js
var foo = ['a', 'b'],
    bar = ['b', 'd'];

append(foo, bar); // ['a', 'b', 'b', 'd']
```

```js
// jinja2 with markdown :)
{% for x in range(10) -%}
    {{ x }}
{% endfor %}
```

This is a [link to the homepage]({{ url_for('render_page')}})

