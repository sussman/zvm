#
# A class which represents the CPU itself, the brain of the virtual
# machine. It ties all the systems together and runs the story.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import zopdecoder

class ZCpuError(Exception):
    "General exception for Zcpu class"

class ZCpuOpcodeOverlap(ZCpuError):
    "Overlapping opcodes registered"

class ZCpuIllegalInstruction(ZCpuError):
    "Illegal instruction encountered"

class ZCpuUnimplementedInstruction(ZCpuError):
    "Unimplemented instruction encountered"

class ZCpu(object):
    def __init__(self, zmem, zopdecoder, zstack, zobjects):
        self._memory = zmem
        self._opdecoder = zopdecoder
        self._stackmanager = zstack
        self._objects = zobjects

    def _get_handler(self, opcode_class, opcode_number):
        try:
            opcode_decl = self.opcodes[opcode_class][opcode_number]
        except IndexError:
            opcode_decl = None
        if not opcode_decl:
            raise ZCpuIllegalInstruction

        # If the opcode declaration is a sequence, we have extra
        # thinking to do.
        if not isinstance(opcode_decl, (list, tuple)):
            opcode_func = opcode_decl
        else:
            # We have several different implementations for the
            # opcode, and we need to select the right one based on
            # version.
            if isinstance(opcode_decl[0], (list, tuple)):
                for func,version in opcode_decl:
                    if version <= self._memory.version:
                        opcode_func = func
                        break
            # Only one implementation, check that our machine is
            # recent enough.
            elif opcode_decl[1] <= self._memory.version:
                opcode_func = opcode_decl[0]
            else:
                raise ZCpuIllegalInstruction

        # The following is a hack, based on our policy of only
        # documenting opcodes we implement. If we ever hit an
        # undocumented opcode, we crash with a not implemented
        # error.
        if not opcode_func.__doc__:
            raise ZCpuUnimplementedInstruction(opcode_func)
        return opcode_func

    def _read_variable(self, addr):
        """Return the value of the given variable, which can come from
        the stack, or from a local/global variable.  If it comes from
        the stack, the value is popped from the stack."""
        if addr == 0x0:
            return self._stackmanager.pop_stack()
        elif 0x0 < addr < 0x10:
            return self._stackmanager.get_local_variable(addr - 1)
        else:
            return self._memory.read_global(addr)

    def _write_result(self, result_value, store_addr=None):
        """Write the given result value to the stack or to a
        local/global variable.  Write result_value to the store_addr
        variable, or if None, extract the destination variable from
        the opcode."""
        if store_addr == None:
            result_addr = self._opdecoder.get_store_address()
        else:
            result_addr = store_addr

        if result_addr != None:
            print ">> $%d = %d" % (result_addr, result_value)
            if result_addr == 0x0:
                self._stackmanager.push_stack(result_value)
            elif 0x0 < result_addr < 0x10:
                self._stackmanager.set_local_variable(result_addr - 1,
                                                      result_value)
            else:
                self._memory.write_global(result_addr, result_value)

    def _branch(self, test_result):
        """Retrieve the branch information, and set the instruction
        pointer according to the type of branch and the test_result."""
        branch_cond, branch_offset = self._opdecoder.get_branch_offset()

        if test_result == branch_cond:
            if branch_offset == 0 or branch_offset == 1:
                print ">> Return %d" % branch_offset
                addr = self._stackmanager.finish_routine(branch_offset)
                self._opdecoder.program_counter = addr
            else:
                print ">> Jump +%d" % branch_offset
                self._opdecoder.program_counter += (branch_offset - 2)

    def run(self):
        """The Magic Function that takes little bits and bytes, twirls
        them around, and brings the magic to your screen!"""
        print "Execution started"
        while True:
            try:
                current_pc = self._opdecoder.program_counter
                (opcode_class, opcode_number,
                 operands) = self._opdecoder.get_next_instruction()
                func = self._get_handler(opcode_class, opcode_number)
                print "<0x%x> (%s:%x) %s %s" % (
                    current_pc, zopdecoder.OPCODE_STRINGS[opcode_class],
                    opcode_number, func.__name__,
                    ', '.join([str(x) for x in operands]))

                # The returned function is unbound, so we must pass
                # self to it ourselves.
                func(self, *operands)
            except ZCpuUnimplementedInstruction, e:
                print "<0x%x> (%s:%x) %s %s (???)" % (
                    current_pc, zopdecoder.OPCODE_STRINGS[opcode_class],
                    opcode_number, e.args[0].__name__,
                    ', '.join([str(x) for x in operands]))
                break

    ##
    ## Opcode implementation functions start here.
    ##

    ## 2OP opcodes (opcodes 1-127 and 192-223)
    def op_je(self, *args):
        """Branch if the first argument is equal to any of the
        subsequent arguments."""
        self._branch(args[0] in args[1:])

    def op_jl(self, *args):
        """"""

    def op_jg(self, *args):
        """"""

    def op_dec_chk(self, variable, test_value):
        """Decrement the variable, and branch if the value becomes
        less than test_value."""
        val = self._read_variable(variable)
        val = (val - 1) % 65536
        self._write_result(val, store_addr=variable)
        self._branch(val < test_value)

    def op_inc_chk(self, variable, test_value):
        """Increment the variable, and branch if the value becomes
        greater than the test value."""
        val = self._read_variable(variable)
        val = (val + 1) % 65536
        self._write_result(val, store_addr=variable)
        self._branch(val > test_value)

    def op_jin(self, *args):
        """"""

    def op_test(self, *args):
        """"""

    def op_or(self, *args):
        """"""

    def op_and(self, *args):
        """"""

    def op_test_attr(self, *args):
        """"""

    def op_set_attr(self, *args):
        """"""

    def op_clear_attr(self, *args):
        """"""

    def op_store(self, variable, value):
        """Store the given value to the given variable."""
        self._write_result(value, store_addr=variable)

    def op_insert_obj(self, *args):
        """"""

    def op_loadw(self, base, offset):
        """Store in the given result register the word value at
        (base+2*offset)."""

        val = self._memory.read_word(base + 2*offset)
        self._write_result(val)

    def op_loadb(self, base, offset):
        """Store in the given result register the byte value at
        (base+offset)."""
        val = self._memory[base+offset]
        self._write_result(val)

    def op_get_prop(self, *args):
        """"""

    def op_get_prop_addr(self, *args):
        """"""

    def op_get_next_prop(self, *args):
        """"""

    def op_add(self, *args):
        """Signed 16-bit addition."""
        self._write_result(sum(args) % 65536) # 2**16 - overflow limit

    def op_sub(self, a, b):
        """Signed 16-bit substraction"""
        self._write_result((a - b) % 65536) # 2**16 - overflow limit

    def op_mul(self, *args):
        """Signed 16-bit multiplication."""
        result = reduce(lambda x,y: x*y, args) % 65536
        self._write_result(result)

    def op_div(self, *args):
        """"""

    def op_mod(self, *args):
        """"""

    def op_call_2s(self, *args):
        """"""

    def op_call_2n(self, *args):
        """"""

    def op_set_colour(self, *args):
        """"""

    def op_throw(self, *args):
        """"""

    ## 1OP opcodes (opcodes 128-175)

    def op_jz(self, val):
        """Branch if the val is zero."""
        self._branch(val == 0)

    def op_get_sibling(self, *args):
        """"""

    def op_get_child(self, *args):
        """"""

    def op_get_parent(self, *args):
        """"""

    def op_get_prop_len(self, *args):
        """"""

    def op_inc(self, *args):
        """"""

    def op_dec(self, *args):
        """"""

    def op_print_addr(self, string_byte_address):
        """Print the ZString at the given byte address."""
        import zstring
        z = zstring.ZStringFactory(self._memory)
        print z.get(string_byte_address)

    def op_call_1s(self, *args):
        """"""

    def op_remove_obj(self, *args):
        """"""

    def op_print_obj(self, *args):
        """"""

    def op_ret(self, *args):
        """"""

    def op_jump(self, *args):
        """Jump unconditionally to the given branch offset.  This
        opcode does not follow the usual branch decision algorithm,
        and so we do not call the _branch method to dispatch the call."""
        cond, offset = self._opdecoder.get_branch_offset()
        self._opdecoder.program_counter += (offset - 2)


    def op_print_paddr(self, *args):
        """"""


    def op_load(self, *args):
        """"""


    def op_not(self, *args):
        """"""


    def op_call_1n(self, routine_addr):
        """Call the given routine, and discard the return value."""
        addr = self._memory.packed_address(routine_addr)
        current_addr = self._opdecoder.program_counter
        new_addr = self._stackmanager.start_routine(addr, None,
                                                    current_addr, [])
        print '%x' % new_addr
        self._opdecoder.program_counter = new_addr



    ## 0OP opcodes (opcodes 176-191)

    def op_rtrue(self, *args):
        """"""


    def op_rfalse(self, *args):
        """"""


    def op_print(self, *args):
        """"""


    def op_print_ret(self, *args):
        """"""


    def op_nop(self, *args):
        """"""


    def op_save(self, *args):
        """"""


    def op_save_v4(self, *args):
        """"""


    def op_restore(self, *args):
        """"""


    def op_restore_v4(self, *args):
        """"""


    def op_restart(self, *args):
        """"""


    def op_ret_popped(self, *args):
        """"""


    def op_pop(self, *args):
        """"""


    def op_catch(self, *args):
        """"""


    def op_quit(self, *args):
        """"""


    def op_new_line(self, *args):
        """"""


    def op_show_status(self, *args):
        """"""


    def op_verify(self, *args):
        """"""


    def op_piracy(self, *args):
        """"""


    ## VAR opcodes (opcodes 224-255)

    # call in v1-3
    def op_call(self, routine_addr, *args):
        """Call the routine r1, passing it any of r2, r3, r4 if defined."""
        addr = self._memory.packed_address(routine_addr)
        return_addr = self._opdecoder.get_store_address()
        current_addr = self._opdecoder.program_counter
        new_addr = self._stackmanager.start_routine(addr,
                                                    return_addr,
                                                    current_addr,
                                                    args)
        self._opdecoder.program_counter = new_addr

    def op_call_vs(self, *args):
        """"""

    def op_storew(self, *args):
        """"""


    def op_storeb(self, *args):
        """"""


    def op_put_prop(self, object_number, property_number, value):
        """Set an object's property to the given value."""
        self._objects.set_property(object_number, property_number, value)

    def op_sread(self, *args):
        """Not implemented yet, but documented so that the detection
        code will be foiled."""


    def op_sread_v4(self, *args):
        """"""


    def op_aread(self, *args):
        """"""


    def op_print_char(self, *args):
        """"""


    def op_print_num(self, *args):
        """"""


    def op_random(self, *args):
        """"""


    def op_push(self, *args):
        """"""


    def op_pull(self, *args):
        """"""


    def op_split_window(self, *args):
        """"""


    def op_set_window(self, *args):
        """"""


    def op_call_vs2(self, *args):
        """"""


    def op_erase_window(self, *args):
        """"""


    def op_erase_line(self, *args):
        """"""


    def op_set_cursor(self, *args):
        """"""


    def op_get_cursor(self, *args):
        """"""


    def op_set_text_style(self, *args):
        """"""


    def op_buffer_mode(self, *args):
        """"""


    def op_output_stream(self, *args):
        """"""


    def op_output_stream_v5(self, *args):
        """"""


    def op_input_stream(self, *args):
        """"""


    # This one may have been used prematurely in v3 stories. Keep an
    # eye out for it if we ever get bug reports.
    def op_sound_effect(self, *args):
        """"""


    def op_read_char(self, *args):
        """"""


    def op_scan_table(self, *args):
        """"""


    def op_not_v5(self, *args):
        """"""


    def op_call_vn(self, *args):
        """"""


    def op_call_vn2(self, *args):
        """"""


    def op_tokenize(self, *args):
        """"""


    def op_encode_text(self, *args):
        """"""


    def op_copy_table(self, *args):
        """"""


    def op_print_table(self, *args):
        """"""


    def op_check_arg_count(self, *args):
        """"""


    ## EXT opcodes (opcodes 256-284)

    def op_save_v5(self, *args):
        """"""


    def op_restore_v5(self, *args):
        """"""


    def op_log_shift(self, *args):
        """"""


    def op_art_shift(self, *args):
        """"""


    def op_set_font(self, *args):
        """"""


    def op_save_undo(self, *args):
        """"""


    def op_restore_undo(self, *args):
        """"""


    def op_print_unicode(self, *args):
        """"""


    def op_check_unicode(self, *args):
        """"""

    # Declaration of the opcode tables. In a Z-Machine, opcodes are
    # divided into tables based on the operand type. Within each
    # table, the operand is then indexed by its number. We preserve
    # that organization in this opcode table.
    #
    # The opcode table is a dictionary mapping an operand type to a
    # list of opcodes definitions. Each opcode definition's index in
    # the table is the opcode number within that opcode table.
    #
    # The opcodes are in one of three forms:
    #
    # - If the opcode is available and unchanging in all versions,
    #   then the definition is simply the function implementing the
    #   opcode.
    #
    # - If the opcode is only available as of a certain version
    #   upwards, then the definition is the tuple (opcode_func,
    #   first_version), where first_version is the version of the
    #   Z-machine where the opcode appeared.
    #
    # - If the opcode changes meaning with successive revisions of the
    #   Z-machine, then the definition is a list of the above tuples,
    #   sorted in descending order (tuple with the highest
    #   first_version comes first). If an instruction became illegal
    #   after a given version, it should have a tuple with the opcode
    #   function set to None.

    opcodes = {
        # 2OP opcodes
        zopdecoder.OPCODE_2OP: [
        None,
        op_je,
        op_jl,
        op_jg,
        op_dec_chk,
        op_inc_chk,
        op_jin,
        op_test,
        op_or,
        op_and,
        op_test_attr,
        op_set_attr,
        op_clear_attr,
        op_store,
        op_insert_obj,
        op_loadw,
        op_loadb,
        op_get_prop,
        op_get_prop_addr,
        op_get_next_prop,
        op_add,
        op_sub,
        op_mul,
        op_div,
        op_mod,
        (op_call_2s, 4),
        (op_call_2n, 5),
        (op_set_colour, 5),
        (op_throw, 5),
        ],

        # 1OP opcodes
        zopdecoder.OPCODE_1OP: [
        op_jz,
        op_get_sibling,
        op_get_child,
        op_get_parent,
        op_get_prop_len,
        op_inc,
        op_dec,
        op_print_addr,
        (op_call_1s, 4),
        op_remove_obj,
        op_print_obj,
        op_ret,
        op_jump,
        op_print_paddr,
        op_load,
        [(op_call_1n, 5), (op_not, 1)]
        ],

        # 0OP opcodes
        zopdecoder.OPCODE_0OP: [
        op_rtrue,
        op_rfalse,
        op_print,
        op_print_ret,
        op_nop,
        [(None, 5), (op_save_v4, 4), (op_save, 1)],
        [(None, 5), (op_restore_v4, 4), (op_restore, 1)],
        op_restart,
        op_ret_popped,
        [(op_catch, 5), (op_pop, 1)],
        op_quit,
        op_new_line,
        [(None, 4), (op_show_status, 3)],
        (op_verify, 3),
        None, # Padding. Opcode 0OP:E is the extended opcode marker.
        (op_piracy, 5),
        ],

        # VAR opcodes
        zopdecoder.OPCODE_VAR: [
        [(op_call_vs, 4), (op_call, 1)],
        op_storew,
        op_storeb,
        op_put_prop,
        [(op_aread, 5), (op_sread_v4, 4), (op_sread, 1)],
        op_print_char,
        op_print_num,
        op_random,
        op_push,
        op_pull,
        (op_split_window, 3),
        (op_set_window, 3),
        (op_call_vs2, 4),
        (op_erase_window, 4),
        (op_erase_line, 4),
        (op_set_cursor, 4),
        (op_get_cursor, 4),
        (op_set_text_style, 4),
        (op_buffer_mode, 4),
        [(op_output_stream_v5, 5), (op_output_stream, 3)],
        (op_input_stream, 3),
        (op_sound_effect, 5),
        (op_read_char, 4),
        (op_scan_table, 4),
        (op_not, 5),
        (op_call_vn, 5),
        (op_call_vn2, 5),
        (op_tokenize, 5),
        (op_encode_text, 5),
        (op_copy_table, 5),
        (op_print_table, 5),
        (op_check_arg_count, 5),
        ],

        # EXT opcodes
        zopdecoder.OPCODE_EXT: [
        (op_save_v5, 5),
        (op_restore_v5, 5),
        (op_log_shift, 5),
        (op_art_shift, 5),
        (op_set_font, 5),
        None,
        None,
        None,
        None,
        (op_save_undo, 5),
        (op_restore_undo, 5),
        (op_print_unicode, 5),
        (op_check_unicode, 5)
        ],
        }
