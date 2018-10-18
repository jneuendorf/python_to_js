// This function is used for indexing as well as subscripting with slices because
// we want to enable non-string indices.
function __slice__(object, slice_type, lower, upper=lower, step=1) {
    if (typeof(object.__slice__) === 'function') {
        return object.__slice__(slice_type, lower, upper, step)
    }

    // index
    if (slice_type === 'index') {
        return object[lower]
    }
    // else: slice_type === 'slice' => actual slicing
    // NOTE: Cannot use 'object.slice' if available because Array / String
    // do not support 'step' in their 'slice' methods.
    const result = []
    for (let i = lower; i < upper; i += step) {
        result.push(object[i])
    }
    return result
}


module.exports = {
    __slice__,
}
